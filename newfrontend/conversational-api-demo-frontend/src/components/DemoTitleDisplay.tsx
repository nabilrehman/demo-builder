import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Lightbulb, Target, MessageSquare } from 'lucide-react';

interface DemoTitleDisplayProps {
  title: string;
  executiveSummary: string;
  businessChallenges: string[];
  talkingTrack: string;
}

export const DemoTitleDisplay = ({
  title,
  executiveSummary,
  businessChallenges,
  talkingTrack
}: DemoTitleDisplayProps) => {
  return (
    <div className="space-y-6">
      {/* Demo Title */}
      <div className="text-center py-8 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
        <Badge className="mb-4">Principal Architect Level</Badge>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 px-4 leading-tight">
          {title}
        </h1>
      </div>

      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            Executive Summary
          </CardTitle>
          <CardDescription>High-level value proposition for stakeholders</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-lg text-gray-700 leading-relaxed">
            {executiveSummary}
          </p>
        </CardContent>
      </Card>

      {/* Business Challenges */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-red-500" />
            Business Challenges Addressed
          </CardTitle>
          <CardDescription>Key pain points this demo solves</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {businessChallenges.map((challenge, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </span>
                <p className="text-gray-700 flex-1 pt-0.5">{challenge}</p>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Talking Track */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-blue-500" />
            Talking Track Preview
          </CardTitle>
          <CardDescription>Recommended demo flow and key moments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-gray-800 leading-relaxed italic">
              "{talkingTrack}"
            </p>
          </div>
        </CardContent>
      </Card>

      <Separator className="my-6" />

      {/* Tips Card */}
      <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
        <CardContent className="pt-6">
          <h3 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Demo Tips
          </h3>
          <ul className="text-sm text-amber-800 space-y-1 ml-6 list-disc">
            <li>Use the talking track as a guide, but adapt to your audience's reactions</li>
            <li>Start with executive-level insights, then drill into operational details</li>
            <li>Keep golden queries ready in the Golden Queries tab for easy reference</li>
            <li>Switch to Developer Mode to show the SQL being generated</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
