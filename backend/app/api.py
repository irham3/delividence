import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app import config, queue, store

app = FastAPI(title="Delividence API")

# Frontend berjalan di origin lain (Next.js), jadi CORS wajib. Daftarnya dibatasi
# lewat env supaya produksi tidak terbuka untuk semua origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class CreateRunRequest(BaseModel):
    brief: str = Field(min_length=1, max_length=config.MAX_BRIEF_CHARS)
    # English adalah default. Aturan hackathon mewajibkan aplikasi mendukung
    # bahasa Inggris minimal; Bahasa Indonesia adalah pilihan tambahan.
    output_language: str = "en"

    @field_validator("output_language")
    @classmethod
    def _supported(cls, v):
        v = v.strip().lower()
        if v not in config.SUPPORTED_OUTPUT_LANGUAGES:
            raise ValueError(
                "output_language must be one of %s"
                % (", ".join(config.SUPPORTED_OUTPUT_LANGUAGES),)
            )
        return v


@app.get("/health")
def health():
    return {"status": "ok", "role": "api", "local": config.LOCAL}


@app.post("/runs", status_code=202)
def create_run(req: CreateRunRequest):
    run_id = uuid.uuid4().hex
    store.create_run(run_id, req.brief, req.output_language)
    queue.publish({"run_id": run_id, "round": 1})
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run
