import React, { useState } from "react";
import { useDocuments } from "../context/DocumentContext";
import { compareAPI, Comparison } from "../services/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  FileText,
  ArrowLeftRight,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Progress } from "./ui/progress";

export function DocumentCompare() {
  const { documents } = useDocuments();
  const [doc1Id, setDoc1Id] = useState<string>("");
  const [doc2Id, setDoc2Id] = useState<string>("");
  const [comparing, setComparing] = useState(false);
  const [comparison, setComparison] =
    useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!doc1Id || !doc2Id) return;

    setComparing(true);
    setError(null);
    setComparison(null);

    try {
      const result = await compareAPI.compareDocuments(
        doc1Id,
        doc2Id,
        {
          comparisonType: "full",
          highlightChanges: true,
        },
      );

      setComparison(result.comparison);
    } catch (err: any) {
      console.error("Failed to compare documents:", err);
      setError(err.message || "Failed to compare documents");
    } finally {
      setComparing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024)
      return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const truncateFilename = (
    filename: string,
    maxLength: number = 25,
  ) => {
    if (filename.length <= maxLength) return filename;
    const extension = filename.substring(
      filename.lastIndexOf("."),
    );
    const nameWithoutExt = filename.substring(
      0,
      filename.lastIndexOf("."),
    );
    const truncatedName = nameWithoutExt.substring(
      0,
      maxLength - extension.length - 3,
    );
    return `${truncatedName}...${extension}`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Compare Documents</CardTitle>
        <CardDescription>
          Select two documents to compare their content and find
          similarities or differences
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm">First Document</label>
            <Select value={doc1Id} onValueChange={setDoc1Id}>
              <SelectTrigger>
                <SelectValue placeholder="Select a document" />
              </SelectTrigger>
              <SelectContent>
                {documents.map((doc) => (
                  <SelectItem
                    key={doc.id}
                    value={doc.id}
                    disabled={doc.id === doc2Id}
                  >
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      <span className="truncate">
                        {truncateFilename(doc.name)}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm">Second Document</label>
            <Select value={doc2Id} onValueChange={setDoc2Id}>
              <SelectTrigger>
                <SelectValue placeholder="Select a document" />
              </SelectTrigger>
              <SelectContent>
                {documents.map((doc) => (
                  <SelectItem
                    key={doc.id}
                    value={doc.id}
                    disabled={doc.id === doc1Id}
                  >
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      <span className="truncate">
                        {truncateFilename(doc.name)}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button
          onClick={handleCompare}
          disabled={!doc1Id || !doc2Id || comparing}
          className="w-full"
        >
          {comparing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Comparing Documents...
            </>
          ) : (
            <>
              <ArrowLeftRight className="w-4 h-4 mr-2" />
              Compare Documents
            </>
          )}
        </Button>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {comparison && (
          <div className="space-y-4 pt-4 border-t">
            <div className="flex items-center justify-between">
              <h3 className="text-lg">Comparison Results</h3>
              <Badge
                variant={
                  comparison.status === "completed"
                    ? "default"
                    : "secondary"
                }
              >
                {comparison.status}
              </Badge>
            </div>

            {comparison.summary && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl text-green-700">
                    {comparison.summary.additions}
                  </div>
                  <div className="text-sm text-green-600">
                    Additions
                  </div>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl text-red-700">
                    {comparison.summary.deletions}
                  </div>
                  <div className="text-sm text-red-600">
                    Deletions
                  </div>
                </div>
                <div className="p-4 bg-yellow-50 rounded-lg">
                  <div className="text-2xl text-yellow-700">
                    {comparison.summary.modifications}
                  </div>
                  <div className="text-sm text-yellow-600">
                    Modifications
                  </div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl text-blue-700">
                    {comparison.summary.totalChanges}
                  </div>
                  <div className="text-sm text-blue-600">
                    Total Changes
                  </div>
                </div>
              </div>
            )}

            {comparison.summary && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Similarity Score</span>
                  <span>
                    {(
                      comparison.summary.similarityScore * 100
                    ).toFixed(1)}
                    %
                  </span>
                </div>
                <Progress
                  value={
                    comparison.summary.similarityScore * 100
                  }
                />
              </div>
            )}

            {comparison.changes &&
              comparison.changes.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm">Key Changes:</h4>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {comparison.changes
                      .slice(0, 10)
                      .map((change: any) => (
                        <div
                          key={change.id}
                          className="p-3 border rounded-lg"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge
                                  variant={
                                    change.type === "addition"
                                      ? "default"
                                      : change.type ===
                                          "deletion"
                                        ? "destructive"
                                        : "secondary"
                                  }
                                >
                                  {change.type}
                                </Badge>
                                {change.severity && (
                                  <Badge variant="outline">
                                    {change.severity}
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm text-gray-700">
                                {change.content}
                              </p>
                              {change.location && (
                                <p className="text-xs text-gray-500 mt-1">
                                  Page {change.location.page} -{" "}
                                  {change.location.section}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

            {comparison.diffUrl && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() =>
                    window.open(comparison.diffUrl, "_blank")
                  }
                >
                  View Diff Document
                </Button>
                {comparison.sideBySideUrl && (
                  <Button
                    variant="outline"
                    onClick={() =>
                      window.open(
                        comparison.sideBySideUrl,
                        "_blank",
                      )
                    }
                  >
                    View Side-by-Side
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        {!comparison && !comparing && doc1Id && doc2Id && (
          <div className="text-center py-8 text-gray-500">
            <ArrowLeftRight className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>
              Click "Compare Documents" to analyze differences
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
