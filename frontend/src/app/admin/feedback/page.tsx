"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw } from "lucide-react";
import { FeedbackStatsCards } from "@/components/admin/FeedbackStats";
import { FeedbackChart } from "@/components/admin/FeedbackChart";
import { FeedbackTable } from "@/components/admin/FeedbackTable";
import { feedbackService } from "@/services/feedbackService";
import { Feedback, FeedbackStats } from "@/types/feedback";
import { useToast } from "@/components/ui/use-toast";

export default function AdminFeedbackPage() {
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const fetchData = async (filters?: any) => {
    try {
      setLoading(true);
      const [statsData, feedbacksData] = await Promise.all([
        feedbackService.getStats(filters),
        feedbackService.getAllFeedbacks(filters)
      ]);
      setStats(statsData);
      setFeedbacks(feedbacksData);
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de charger les données de feedback",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFilterChange = (filters: any) => {
    fetchData(filters);
  };

  const exportToCSV = () => {
    const headers = ["ID", "User ID", "User Type", "Rating", "Quality", "Version", "Comment", "Date"];
    const csvData = feedbacks.map(f => [
      f.id,
      f.user_id,
      f.user_type,
      f.rating,
      f.match_quality,
      f.algorithm_version,
      f.comment || "",
      new Date(f.created_at).toLocaleDateString()
    ]);
    
    const csvContent = [
      headers.join(","),
      ...csvData.map(row => row.map(cell => `"${cell}"`).join(","))
    ].join("\n");
    
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `feedbacks_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Dashboard Feedback</h1>
          <p className="text-muted-foreground">
            Analyse des retours utilisateurs sur les matchings
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => fetchData()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualiser
          </Button>
          <Button onClick={exportToCSV}>
            <Download className="h-4 w-4 mr-2" />
            Exporter CSV
          </Button>
        </div>
      </div>

      {stats && (
        <>
          <FeedbackStatsCards stats={stats} />
          <div className="mt-8">
            <FeedbackChart stats={stats} />
          </div>
        </>
      )}

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Tous les feedbacks</h2>
        <FeedbackTable feedbacks={feedbacks} onFilterChange={handleFilterChange} />
      </div>
    </div>
  );
}