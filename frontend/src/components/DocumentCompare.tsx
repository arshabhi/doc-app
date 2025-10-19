import React, { useState } from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { FileText, ArrowLeftRight, Loader2 } from 'lucide-react';
import { Badge } from './ui/badge';

export function DocumentCompare() {
  const { documents } = useDocuments();
  const [doc1Id, setDoc1Id] = useState<string>('');
  const [doc2Id, setDoc2Id] = useState<string>('');
  const [comparing, setComparing] = useState(false);
  const [comparison, setComparison] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!doc1Id || !doc2Id) return;

    setComparing(true);
    // Mock comparison delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    const doc1 = documents.find(d => d.id === doc1Id);
    const doc2 = documents.find(d => d.id === doc2Id);

    const mockComparison = `
**Comparison Results:**

**Document 1:** ${doc1?.name}
**Document 2:** ${doc2?.name}

**Key Differences:**
- Document 1 focuses on ${doc1?.name.includes('Research') ? 'research methodologies' : 'business strategies'}
- Document 2 emphasizes ${doc2?.name.includes('Research') ? 'research methodologies' : 'business strategies'}

**Similarities:**
- Both documents discuss technology and innovation
- Similar document structure and formatting
- Comparable length and complexity

**Content Analysis:**
- Document 1 has a more ${Math.random() > 0.5 ? 'technical' : 'general'} approach
- Document 2 provides ${Math.random() > 0.5 ? 'more detailed examples' : 'broader overview'}

**Recommendations:**
- Use Document 1 for ${doc1?.name.split('.')[0].toLowerCase()} purposes
- Use Document 2 for ${doc2?.name.split('.')[0].toLowerCase()} purposes

[This is a mock comparison. A real implementation would use AI to analyze and compare the actual document contents.]
    `;

    setComparison(mockComparison);
    setComparing(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Compare Documents</CardTitle>
        <CardDescription>
          Select two documents to compare their content and find similarities or differences
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
                  <SelectItem key={doc.id} value={doc.id} disabled={doc.id === doc2Id}>
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      {doc.name}
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
                  <SelectItem key={doc.id} value={doc.id} disabled={doc.id === doc1Id}>
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      {doc.name}
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

        {comparison && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-2">
              <Badge>Comparison Results</Badge>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg border">
              <pre className="text-sm whitespace-pre-wrap">{comparison}</pre>
            </div>
          </div>
        )}

        {!comparison && !comparing && documents.length >= 2 && (
          <div className="text-center py-8 text-gray-500">
            <ArrowLeftRight className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>Select two documents to start comparing</p>
          </div>
        )}

        {documents.length < 2 && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>You need at least 2 documents to use comparison</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
