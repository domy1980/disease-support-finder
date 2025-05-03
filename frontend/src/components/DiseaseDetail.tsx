import { useEffect, useState } from "react";
import { DiseaseWithOrganizations, SupportOrganization } from "../types";
import { fetchOrganizations } from "../services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { ArrowLeft } from "lucide-react";
import { OrganizationList } from "./OrganizationList";

interface DiseaseDetailProps {
  diseaseWithOrgs: DiseaseWithOrganizations;
  onBack: () => void;
  isLoading?: boolean;
}

export function DiseaseDetail({ diseaseWithOrgs, onBack, isLoading: parentIsLoading = false }: DiseaseDetailProps) {
  const [organizations, setOrganizations] = useState<SupportOrganization[]>(
    diseaseWithOrgs.organizations || []
  );
  const [isLoadingOrgs, setIsLoadingOrgs] = useState(diseaseWithOrgs.organizations.length === 0);
  const { disease } = diseaseWithOrgs;

  useEffect(() => {
    if (diseaseWithOrgs.organizations.length === 0) {
      const loadOrganizations = async () => {
        try {
          setIsLoadingOrgs(true);
          const data = await fetchOrganizations(disease.disease_id);
          setOrganizations(data);
        } catch (error) {
          console.error("Error fetching organizations:", error);
        } finally {
          setIsLoadingOrgs(false);
        }
      };

      loadOrganizations();
    } else {
      setOrganizations(diseaseWithOrgs.organizations);
      setIsLoadingOrgs(false);
    }
  }, [disease.disease_id, diseaseWithOrgs.organizations]);

  return (
    <div className="space-y-6">
      <Button variant="outline" onClick={onBack} className="mb-4">
        <ArrowLeft className="h-4 w-4 mr-2" />
        戻る
      </Button>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap gap-2 mb-2">
            {disease.is_intractable && (
              <Badge variant="secondary">指定難病</Badge>
            )}
            {disease.is_childhood_chronic && (
              <Badge variant="outline">小児慢性特定疾病</Badge>
            )}
          </div>
          <CardTitle className="text-2xl">{disease.name_ja}</CardTitle>
          {disease.name_en && (
            <CardDescription className="text-lg">{disease.name_en}</CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {disease.synonyms_ja && disease.synonyms_ja.length > 0 && (
            <div>
              <h3 className="text-sm font-medium mb-1">類義語（日本語）:</h3>
              <div className="flex flex-wrap gap-1">
                {disease.synonyms_ja.map((synonym, index) => (
                  <Badge key={index} variant="outline">
                    {synonym}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {disease.synonyms_en && disease.synonyms_en.length > 0 && (
            <div>
              <h3 className="text-sm font-medium mb-1">類義語（英語）:</h3>
              <div className="flex flex-wrap gap-1">
                {disease.synonyms_en.map((synonym, index) => (
                  <Badge key={index} variant="outline">
                    {synonym}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">関連団体</h2>
        <OrganizationList organizations={organizations} isLoading={isLoadingOrgs || parentIsLoading} />
      </div>
    </div>
  );
}
