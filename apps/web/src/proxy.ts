import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// Pages réservées aux personnes connectées. ATTENTION : ce proxy ne fait que de l'ergonomie
// (renvoyer vers la connexion). La vraie protection est dans le backend, qui vérifie le
// jeton à chaque appel d'API ; le rôle admin n'est JAMAIS décidé ici.
const isProtectedPage = createRouteMatcher(["/account(.*)", "/onboarding(.*)", "/admin(.*)"]);

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedPage(request)) await auth.protect();
});

export const config = {
  matcher: [
    // Tout sauf les fichiers internes de Next et les fichiers statiques.
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
