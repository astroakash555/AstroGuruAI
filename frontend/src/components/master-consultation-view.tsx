import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface MasterConsultationSection {
  section_id: string;
  title: string;
  paragraphs?: string[];
  body?: string;
}

export interface MasterConsultationPayload {
  language?: string;
  sections: MasterConsultationSection[];
}

interface MasterConsultationViewProps {
  consultation: MasterConsultationPayload | null | undefined;
}

export function MasterConsultationView({ consultation }: MasterConsultationViewProps) {
  const sections = consultation?.sections ?? [];

  if (!sections.length) {
    return (
      <Card>
        <CardContent className="py-8 text-sm text-muted-foreground">
          इस रिपोर्ट के लिए अभी परामर्श उपलब्ध नहीं है।
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {sections.map((section, index) => {
        const paragraphs =
          section.paragraphs?.filter(Boolean) ??
          (section.body ? section.body.split("\n\n").filter(Boolean) : []);

        return (
          <Card key={section.section_id || `section-${index}`}>
            <CardHeader>
              <CardTitle className="text-lg">{section.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm leading-7">
              {paragraphs.map((paragraph, paragraphIndex) => (
                <p key={`${section.section_id}-${paragraphIndex}`}>{paragraph}</p>
              ))}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
