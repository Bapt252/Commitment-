import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart2, MessageSquare, Star, Users } from "lucide-react";
import { FeedbackStats } from "@/types/feedback";

interface FeedbackStatsProps {
  stats: FeedbackStats;
}

export function FeedbackStatsCards({ stats }: FeedbackStatsProps) {
  const satisfactionRate = ((stats.average_rating / 5) * 100).toFixed(1);
  
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Note moyenne</CardTitle>
          <Star className="h-4 w-4 text-yellow-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.average_rating.toFixed(1)}/5</div>
          <p className="text-xs text-muted-foreground">
            Sur {stats.total_feedbacks} retours
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Taux de satisfaction</CardTitle>
          <BarChart2 className="h-4 w-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{satisfactionRate}%</div>
          <p className="text-xs text-muted-foreground">
            Basé sur la moyenne des notes
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total feedbacks</CardTitle>
          <MessageSquare className="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_feedbacks}</div>
          <p className="text-xs text-muted-foreground">
            Depuis le lancement
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Dernier feedback</CardTitle>
          <Users className="h-4 w-4 text-purple-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats.latest_feedback_date ? 
              new Date(stats.latest_feedback_date).toLocaleDateString() : 
              "Aucun"}
          </div>
          <p className="text-xs text-muted-foreground">
            Date du dernier retour
          </p>
        </CardContent>
      </Card>
    </div>
  );
}