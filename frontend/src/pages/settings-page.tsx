import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { useTheme } from "@/providers/theme-provider";

export function SettingsPage() {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">Appearance, session, and API configuration.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Switch between light and dark themes.</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-between">
          <Label htmlFor="dark-mode">Dark mode</Label>
          <Switch
            id="dark-mode"
            checked={theme === "dark"}
            onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Session</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p><span className="font-medium">Signed in as:</span> {user?.email}</p>
          <p><span className="font-medium">Auth mode:</span> Local demo token (backend auth pending)</p>
          <Button variant="outline" onClick={logout}>Sign out</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>API</CardTitle>
          <CardDescription>Configured through Vite environment variables.</CardDescription>
        </CardHeader>
        <CardContent className="text-sm">
          <p><span className="font-medium">Base URL:</span> {import.meta.env.VITE_API_BASE_URL ?? "/api/v1"}</p>
        </CardContent>
      </Card>
    </div>
  );
}
