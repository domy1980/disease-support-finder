import React, { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";

interface SearchBarProps {
  onSearch: (query: string, includeSynonyms: boolean) => void;
  isLoading: boolean;
}

export function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [includeSynonyms, setIncludeSynonyms] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, includeSynonyms);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      <div className="flex w-full max-w-3xl items-center space-x-2">
        <Input
          type="text"
          placeholder="病名を入力してください..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
              <span>検索中...</span>
            </div>
          ) : (
            <>
              <Search className="mr-2 h-4 w-4" />
              <span>検索</span>
            </>
          )}
        </Button>
      </div>
      <div className="flex items-center space-x-2">
        <Checkbox
          id="includeSynonyms"
          checked={includeSynonyms}
          onCheckedChange={(checked) => setIncludeSynonyms(checked as boolean)}
        />
        <Label htmlFor="includeSynonyms">類義語も含めて検索する</Label>
      </div>
    </form>
  );
}
