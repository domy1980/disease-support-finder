import React, { useState } from 'react';
import { ManualEntryRequest, ManualOrganizationRequest } from '../types';
import { addManualEntry, addManualOrganization } from '../services/api';

interface ManualEntryFormProps {
  diseaseId: string;
  diseaseName: string;
  onEntryAdded: () => void;
}

export const ManualEntryForm = ({ diseaseId, diseaseName, onEntryAdded }: ManualEntryFormProps) => {
  const [activeTab, setActiveTab] = useState<'organization' | 'note'>('organization');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [orgName, setOrgName] = useState('');
  const [orgUrl, setOrgUrl] = useState('');
  const [orgType, setOrgType] = useState<'patient' | 'family' | 'support'>('support');
  const [orgDescription, setOrgDescription] = useState('');
  const [orgNotes, setOrgNotes] = useState('');
  
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [noteUrl, setNoteUrl] = useState('');
  const [noteType, setNoteType] = useState('note');

  const handleAddOrganization = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!orgName || !orgUrl) {
      setError('団体名とURLは必須です。');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);
      setSuccess(null);
      
      const orgRequest: ManualOrganizationRequest = {
        disease_id: diseaseId,
        name: orgName,
        url: orgUrl,
        type: orgType,
        description: orgDescription || undefined,
        notes: orgNotes || undefined
      };
      
      await addManualOrganization(orgRequest);
      
      setOrgName('');
      setOrgUrl('');
      setOrgType('support');
      setOrgDescription('');
      setOrgNotes('');
      
      setSuccess('団体情報が追加されました。');
      onEntryAdded();
    } catch (err) {
      setError('団体情報の追加中にエラーが発生しました。');
      console.error('Error adding organization:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!noteTitle || !noteContent) {
      setError('タイトルと内容は必須です。');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);
      setSuccess(null);
      
      const noteRequest: ManualEntryRequest = {
        disease_id: diseaseId,
        title: noteTitle,
        content: noteContent,
        url: noteUrl || undefined,
        entry_type: noteType
      };
      
      await addManualEntry(noteRequest);
      
      setNoteTitle('');
      setNoteContent('');
      setNoteUrl('');
      setNoteType('note');
      
      setSuccess('メモが追加されました。');
      onEntryAdded();
    } catch (err) {
      setError('メモの追加中にエラーが発生しました。');
      console.error('Error adding note:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full border rounded-lg p-4 bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-4">
        {diseaseName} に情報を追加
      </h3>
      
      <div className="flex border-b mb-4">
        <button
          className={`px-4 py-2 ${activeTab === 'organization' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
          onClick={() => setActiveTab('organization')}
        >
          団体情報
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'note' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
          onClick={() => setActiveTab('note')}
        >
          メモ・その他情報
        </button>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded">
          {success}
        </div>
      )}
      
      {activeTab === 'organization' ? (
        <form onSubmit={handleAddOrganization} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">団体名 *</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">URL *</label>
            <input
              type="url"
              className="w-full px-3 py-2 border rounded-md"
              value={orgUrl}
              onChange={(e) => setOrgUrl(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">団体タイプ</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={orgType}
              onChange={(e) => setOrgType(e.target.value as 'patient' | 'family' | 'support')}
            >
              <option value="patient">患者会</option>
              <option value="family">家族会</option>
              <option value="support">支援団体</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">説明</label>
            <textarea
              className="w-full px-3 py-2 border rounded-md"
              rows={3}
              value={orgDescription}
              onChange={(e) => setOrgDescription(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">メモ</label>
            <textarea
              className="w-full px-3 py-2 border rounded-md"
              rows={2}
              value={orgNotes}
              onChange={(e) => setOrgNotes(e.target.value)}
            />
          </div>
          
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            disabled={isSubmitting}
          >
            {isSubmitting ? '追加中...' : '団体を追加'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleAddNote} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">タイトル *</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md"
              value={noteTitle}
              onChange={(e) => setNoteTitle(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">内容 *</label>
            <textarea
              className="w-full px-3 py-2 border rounded-md"
              rows={5}
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">関連URL</label>
            <input
              type="url"
              className="w-full px-3 py-2 border rounded-md"
              value={noteUrl}
              onChange={(e) => setNoteUrl(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">情報タイプ</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={noteType}
              onChange={(e) => setNoteType(e.target.value)}
            >
              <option value="note">一般メモ</option>
              <option value="contact">連絡先情報</option>
              <option value="resource">参考資料</option>
              <option value="event">イベント情報</option>
            </select>
          </div>
          
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            disabled={isSubmitting}
          >
            {isSubmitting ? '追加中...' : 'メモを追加'}
          </button>
        </form>
      )}
    </div>
  );
};
