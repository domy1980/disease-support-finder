import { SupportOrganization } from "../types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { ExternalLink } from "lucide-react";

interface OrganizationListProps {
  organizations: SupportOrganization[];
  isLoading: boolean;
}

export function OrganizationList({ organizations, isLoading }: OrganizationListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
        <span className="ml-2">団体情報を取得中...</span>
      </div>
    );
  }

  if (organizations.length === 0) {
    return (
      <div className="text-center p-8 border rounded-lg bg-muted/50">
        <p>支援団体が見つかりませんでした。</p>
        <p className="text-sm text-muted-foreground mt-2">
          この疾患に関連する団体情報は現在収集中です。後ほど再度お試しください。
        </p>
      </div>
    );
  }

  const groupedOrganizations = {
    patient: organizations.filter(org => org.type === "patient"),
    family: organizations.filter(org => org.type === "family"),
    support: organizations.filter(org => org.type === "support")
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "patient": return "患者会";
      case "family": return "家族会";
      case "support": return "支援団体";
      default: return "その他";
    }
  };

  return (
    <div className="space-y-6">
      {Object.entries(groupedOrganizations).map(([type, orgs]) => {
        if (orgs.length === 0) return null;
        
        return (
          <div key={type} className="space-y-3">
            <h3 className="text-lg font-semibold">{getTypeLabel(type)}</h3>
            <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
              {orgs.map((org, index) => (
                <Card key={index}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base">{org.name}</CardTitle>
                      <Badge variant="outline">{getTypeLabel(org.type)}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {org.description && (
                      <CardDescription className="mb-2 line-clamp-2">
                        {org.description}
                      </CardDescription>
                    )}
                    <a 
                      href={org.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center text-sm text-primary hover:underline"
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      ウェブサイトを訪問
                    </a>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
