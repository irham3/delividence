import { AuthRoute } from "@/components/delividence/auth-route";

export default async function RegisterPage({ searchParams }: PageProps<"/register">) {
  const params = await searchParams;
  const destination = typeof params.next === "string" ? params.next : undefined;
  return <AuthRoute register destination={destination} />;
}
