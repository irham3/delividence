import { AuthRoute } from "@/components/delividence/auth-route";

export default async function SignInPage({ searchParams }: PageProps<"/sign-in">) {
  const params = await searchParams;
  const destination = typeof params.next === "string" ? params.next : undefined;
  return <AuthRoute destination={destination} />;
}
