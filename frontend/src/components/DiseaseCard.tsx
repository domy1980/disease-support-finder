import { DiseaseInfo } from "../types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";

interface DiseaseCardProps {
  disease: DiseaseInfo;
  onClick: (diseaseId: string) => void;
}

export function DiseaseCard({ disease, onClick }: DiseaseCardProps) {
  return (
    <Card 
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(disease.disease_id)}
    >
      <CardHeader>
        <CardTitle className="text-lg font-bold">{disease.name_ja}</CardTitle>
        {disease.name_en && (
          <CardDescription>{disease.name_en}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-2">
          {disease.is_intractable && (
            <Badge variant="secondary">指定難病</Badge>
          )}
          {disease.is_childhood_chronic && (
            <Badge variant="outline">小児慢性特定疾病</Badge>
          )}
        </div>
        
        {disease.synonyms_ja && disease.synonyms_ja.length > 0 && (
          <div className="mt-2">
            <p className="text-sm font-medium">類義語（日本語）:</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {disease.synonyms_ja.map((synonym, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {synonym}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
