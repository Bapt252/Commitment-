import { Feedback } from "@/types/feedback";

export const exportFeedbacksToCSV = (feedbacks: Feedback[]) => {
  const headers = [
    "ID",
    "Match ID",
    "User ID",
    "User Type",
    "Rating",
    "Quality",
    "Algorithm Version",
    "Comment",
    "Created At"
  ];
  
  const rows = feedbacks.map(feedback => [
    feedback.id,
    feedback.match_id,
    feedback.user_id,
    feedback.user_type,
    feedback.rating,
    feedback.match_quality,
    feedback.algorithm_version,
    feedback.comment || "",
    new Date(feedback.created_at).toISOString()
  ]);
  
  const csvContent = [
    headers.join(","),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(","))
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