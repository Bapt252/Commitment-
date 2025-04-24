import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import { Feedback } from "@/types/feedback";
import { 
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

interface FeedbackTableProps {
  feedbacks: Feedback[];
  onFilterChange: (filters: any) => void;
}

export function FeedbackTable({ feedbacks, onFilterChange }: FeedbackTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [filters, setFilters] = useState({
    algorithm_version: "",
    min_rating: "",
    user_type: "",
  });

  const toggleRow = (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return "bg-green-100 text-green-800";
    if (rating >= 3) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4">
        <Select
          value={filters.algorithm_version}
          onValueChange={(value) => {
            setFilters({ ...filters, algorithm_version: value });
            onFilterChange({ ...filters, algorithm_version: value });
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Version algorithme" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes versions</SelectItem>
            <SelectItem value="v1.0.0">v1.0.0</SelectItem>
            <SelectItem value="v1.1.0">v1.1.0</SelectItem>
          </SelectContent>
        </Select>
        
        <Select
          value={filters.user_type}
          onValueChange={(value) => {
            setFilters({ ...filters, user_type: value });
            onFilterChange({ ...filters, user_type: value });
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Type utilisateur" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous</SelectItem>
            <SelectItem value="recruiter">Recruteur</SelectItem>
            <SelectItem value="candidate">Candidat</SelectItem>
          </SelectContent>
        </Select>
        
        <Input
          type="number"
          placeholder="Note minimale"
          className="w-[180px]"
          value={filters.min_rating}
          onChange={(e) => {
            setFilters({ ...filters, min_rating: e.target.value });
            onFilterChange({ ...filters, min_rating: e.target.value });
          }}
        />
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Utilisateur</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Note</TableHead>
              <TableHead>Qualité</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {feedbacks.map((feedback) => (
              <Collapsible key={feedback.id} asChild>
                <>
                  <TableRow>
                    <TableCell className="font-medium">{feedback.id.slice(0, 8)}...</TableCell>
                    <TableCell>{feedback.user_id.slice(0, 8)}...</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {feedback.user_type === "recruiter" ? "Recruteur" : "Candidat"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getRatingColor(feedback.rating)}>
                        {feedback.rating}/5
                      </Badge>
                    </TableCell>
                    <TableCell>{feedback.match_quality}</TableCell>
                    <TableCell>{feedback.algorithm_version}</TableCell>
                    <TableCell>{new Date(feedback.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      {feedback.comment && (
                        <CollapsibleTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRow(feedback.id)}
                          >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            {expandedRows.has(feedback.id) ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )}
                          </Button>
                        </CollapsibleTrigger>
                      )}
                    </TableCell>
                  </TableRow>
                  {feedback.comment && (
                    <CollapsibleContent asChild>
                      <TableRow>
                        <TableCell colSpan={8} className="bg-muted/50">
                          <div className="p-4">
                            <h4 className="font-semibold mb-2">Commentaire :</h4>
                            <p className="text-sm">{feedback.comment}</p>
                          </div>
                        </TableCell>
                      </TableRow>
                    </CollapsibleContent>
                  )}
                </>
              </Collapsible>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}