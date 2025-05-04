import React, { useState, useEffect } from 'react';
import { Box, Button, TextField, Typography, Paper, Grid, IconButton, Chip, FormControlLabel, Switch, CircularProgress, Alert } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import { useParams } from 'react-router-dom';
import { fetchSearchConfig, updateSearchConfig, addSearchTerm, updateSearchTerm, deleteSearchTerm } from '../services/api_search_terms';

interface SearchTerm {
  id: string;
  term: string;
  language: string;
  type: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

interface SearchConfig {
  disease_id: string;
  search_terms: SearchTerm[];
  max_token_limit: number;
  use_approximate_matching: boolean;
  two_step_validation: boolean;
  require_human_verification: boolean;
  last_updated: string;
}

interface SearchTermEditorProps {
  diseaseId?: string;
}

const SearchTermEditor: React.FC<SearchTermEditorProps> = ({ diseaseId: propsDiseaseId }) => {
  const { diseaseId: routeDiseaseId } = useParams<{ diseaseId: string }>();
  const diseaseId = propsDiseaseId || routeDiseaseId;
  const [config, setConfig] = useState<SearchConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [newTerm, setNewTerm] = useState('');
  const [newLanguage, setNewLanguage] = useState('ja');
  const [newType, setNewType] = useState('patient');
  
  const [editingTerm, setEditingTerm] = useState<SearchTerm | null>(null);
  const [editedTerm, setEditedTerm] = useState('');
  
  useEffect(() => {
    if (diseaseId) {
      loadSearchConfig();
    }
  }, [diseaseId]);
  
  const loadSearchConfig = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchSearchConfig(diseaseId || '');
      setConfig(data);
    } catch (err) {
      setError('検索設定の読み込み中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddTerm = async () => {
    if (!newTerm.trim()) {
      setError('検索語を入力してください。');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await addSearchTerm(diseaseId || '', {
        term: newTerm,
        language: newLanguage,
        type: newType
      });
      
      setSuccess('検索語が追加されました。');
      setNewTerm('');
      loadSearchConfig();
    } catch (err) {
      setError('検索語の追加中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleUpdateTerm = async () => {
    if (!editingTerm || !editedTerm.trim()) {
      setError('検索語を入力してください。');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await updateSearchTerm(diseaseId || '', editingTerm.id, {
        term: editedTerm
      });
      
      setSuccess('検索語が更新されました。');
      setEditingTerm(null);
      loadSearchConfig();
    } catch (err) {
      setError('検索語の更新中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteTerm = async (termId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await deleteSearchTerm(diseaseId || '', termId);
      
      setSuccess('検索語が削除されました。');
      loadSearchConfig();
    } catch (err) {
      setError('検索語の削除中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleToggleEnabled = async (term: SearchTerm) => {
    setLoading(true);
    setError(null);
    
    try {
      await updateSearchTerm(diseaseId || '', term.id, {
        enabled: !term.enabled
      });
      
      setSuccess('検索語の状態が更新されました。');
      loadSearchConfig();
    } catch (err) {
      setError('検索語の状態更新中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleUpdateConfig = async (field: string, value: boolean) => {
    if (!config) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const updatedConfig = { ...config, [field]: value };
      await updateSearchConfig(diseaseId || '', { [field]: value });
      
      setSuccess('検索設定が更新されました。');
      setConfig(updatedConfig);
    } catch (err) {
      setError('検索設定の更新中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'patient':
        return 'primary';
      case 'family':
        return 'secondary';
      case 'support':
        return 'success';
      default:
        return 'default';
    }
  };
  
  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'patient':
        return '患者会';
      case 'family':
        return '家族会';
      case 'support':
        return '支援団体';
      default:
        return type;
    }
  };
  
  const getLanguageLabel = (language: string) => {
    return language === 'ja' ? '日本語' : '英語';
  };
  
  if (loading && !config) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error && !config) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        検索語の編集
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          検索設定
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <FormControlLabel
              control={
                <Switch
                  checked={config?.use_approximate_matching || false}
                  onChange={() => handleUpdateConfig('use_approximate_matching', !config?.use_approximate_matching)}
                  disabled={loading}
                />
              }
              label="近似マッチングを使用"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <FormControlLabel
              control={
                <Switch
                  checked={config?.two_step_validation || false}
                  onChange={() => handleUpdateConfig('two_step_validation', !config?.two_step_validation)}
                  disabled={loading}
                />
              }
              label="二段階検証を使用"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <FormControlLabel
              control={
                <Switch
                  checked={config?.require_human_verification || false}
                  onChange={() => handleUpdateConfig('require_human_verification', !config?.require_human_verification)}
                  disabled={loading}
                />
              }
              label="人間による検証を必須にする"
            />
          </Grid>
        </Grid>
      </Paper>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          検索語の追加
        </Typography>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              label="検索語"
              value={newTerm}
              onChange={(e) => setNewTerm(e.target.value)}
              disabled={loading}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              select
              label="言語"
              value={newLanguage}
              onChange={(e) => setNewLanguage(e.target.value)}
              disabled={loading}
              SelectProps={{
                native: true
              }}
            >
              <option value="ja">日本語</option>
              <option value="en">英語</option>
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="タイプ"
              value={newType}
              onChange={(e) => setNewType(e.target.value)}
              disabled={loading}
              SelectProps={{
                native: true
              }}
            >
              <option value="patient">患者会</option>
              <option value="family">家族会</option>
              <option value="support">支援団体</option>
              <option value="general">一般</option>
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddTerm}
              disabled={loading || !newTerm.trim()}
            >
              追加
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          検索語一覧
        </Typography>
        
        {config?.search_terms.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            検索語がありません。
          </Typography>
        ) : (
          <Box sx={{ mt: 2 }}>
            {config?.search_terms.map((term) => (
              <Box
                key={term.id}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  p: 1,
                  borderBottom: '1px solid #eee',
                  opacity: term.enabled ? 1 : 0.5
                }}
              >
                {editingTerm?.id === term.id ? (
                  <>
                    <TextField
                      fullWidth
                      value={editedTerm}
                      onChange={(e) => setEditedTerm(e.target.value)}
                      disabled={loading}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    
                    <IconButton
                      color="primary"
                      onClick={handleUpdateTerm}
                      disabled={loading || !editedTerm.trim()}
                      size="small"
                    >
                      <SaveIcon />
                    </IconButton>
                    
                    <IconButton
                      color="default"
                      onClick={() => setEditingTerm(null)}
                      disabled={loading}
                      size="small"
                    >
                      <CancelIcon />
                    </IconButton>
                  </>
                ) : (
                  <>
                    <Typography
                      variant="body1"
                      sx={{
                        flexGrow: 1,
                        textDecoration: term.enabled ? 'none' : 'line-through'
                      }}
                    >
                      {term.term}
                    </Typography>
                    
                    <Chip
                      label={getLanguageLabel(term.language)}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    
                    <Chip
                      label={getTypeLabel(term.type)}
                      color={getTypeColor(term.type) as any}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    
                    <IconButton
                      color="primary"
                      onClick={() => {
                        setEditingTerm(term);
                        setEditedTerm(term.term);
                      }}
                      disabled={loading}
                      size="small"
                    >
                      <EditIcon />
                    </IconButton>
                    
                    <IconButton
                      color={term.enabled ? 'default' : 'primary'}
                      onClick={() => handleToggleEnabled(term)}
                      disabled={loading}
                      size="small"
                    >
                      {term.enabled ? (
                        <span title="無効化">✓</span>
                      ) : (
                        <span title="有効化">○</span>
                      )}
                    </IconButton>
                    
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteTerm(term.id)}
                      disabled={loading}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </>
                )}
              </Box>
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default SearchTermEditor;
