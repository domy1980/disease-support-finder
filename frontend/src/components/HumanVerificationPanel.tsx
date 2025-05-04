import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, Grid, CircularProgress, Alert, Chip, Card, CardContent, Divider, TextField, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { useParams } from 'react-router-dom';
import { fetchOrganizationCollection, validateOrganization } from '../services/api_validation';
import { LLMValidatedOrganization, LLMValidationStatus } from '../types/llm_enhanced';

interface HumanVerificationPanelProps {
  diseaseId?: string;
  onVerificationComplete?: () => void;
}

const HumanVerificationPanel: React.FC<HumanVerificationPanelProps> = ({ 
  diseaseId: propsDiseaseId,
  onVerificationComplete
}) => {
  const { diseaseId: routeDiseaseId } = useParams<{ diseaseId: string }>();
  const diseaseId = propsDiseaseId || routeDiseaseId;
  
  const [organizations, setOrganizations] = useState<LLMValidatedOrganization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [selectedOrg, setSelectedOrg] = useState<LLMValidatedOrganization | null>(null);
  const [verificationNotes, setVerificationNotes] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  
  useEffect(() => {
    if (diseaseId) {
      loadOrganizations();
    }
  }, [diseaseId]);
  
  const loadOrganizations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchOrganizationCollection(diseaseId || '');
      setOrganizations(data.organizations);
    } catch (err) {
      setError('組織データの読み込み中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleOpenDialog = (org: LLMValidatedOrganization) => {
    setSelectedOrg(org);
    setVerificationNotes(org.human_verification_notes || '');
    setDialogOpen(true);
  };
  
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedOrg(null);
    setVerificationNotes('');
  };
  
  const handleVerify = async (approve: boolean) => {
    if (!selectedOrg) return;
    
    setLoading(true);
    setError(null);
    
    try {
      await validateOrganization(diseaseId || '', selectedOrg.id, {
        validation_notes: verificationNotes,
        approve
      });
      
      setSuccess(`組織「${selectedOrg.name}」が${approve ? '承認' : '拒否'}されました。`);
      loadOrganizations();
      handleCloseDialog();
      
      if (onVerificationComplete) {
        onVerificationComplete();
      }
    } catch (err) {
      setError('検証処理中にエラーが発生しました。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const getStatusColor = (status: LLMValidationStatus) => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'extracted':
        return 'info';
      case 'verified':
        return 'warning';
      case 'human_approved':
        return 'success';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };
  
  const getStatusLabel = (status: LLMValidationStatus) => {
    switch (status) {
      case 'pending':
        return '保留中';
      case 'extracted':
        return '抽出済み';
      case 'verified':
        return 'LLM検証済み';
      case 'human_approved':
        return '人間承認済み';
      case 'rejected':
        return '拒否';
      default:
        return status;
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
      case 'medical':
        return '医療機関';
      case 'research':
        return '研究機関';
      case 'government':
        return '行政機関';
      default:
        return 'その他';
    }
  };
  
  const needsVerification = (org: LLMValidatedOrganization) => {
    return org.validation_status === 'verified' && !org.human_verified;
  };
  
  if (loading && organizations.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  const pendingOrgs = organizations.filter(needsVerification);
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        人間による検証
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          検証待ち組織 ({pendingOrgs.length})
        </Typography>
        
        {pendingOrgs.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            検証待ちの組織はありません。
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {pendingOrgs.map((org) => (
              <Grid item xs={12} key={org.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="h6">{org.name}</Typography>
                      <Chip 
                        label={getStatusLabel(org.validation_status)} 
                        color={getStatusColor(org.validation_status) as any}
                        size="small"
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {getTypeLabel(org.organization_type)}
                    </Typography>
                    
                    <Typography variant="body2" gutterBottom>
                      <strong>URL:</strong> <a href={org.url} target="_blank" rel="noopener noreferrer">{org.url}</a>
                    </Typography>
                    
                    {org.description && (
                      <Typography variant="body2" gutterBottom>
                        <strong>説明:</strong> {org.description}
                      </Typography>
                    )}
                    
                    {org.validation_notes && (
                      <>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="body2" gutterBottom>
                          <strong>LLM検証メモ:</strong> {org.validation_notes}
                        </Typography>
                      </>
                    )}
                    
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                      <Button 
                        variant="contained" 
                        color="primary"
                        onClick={() => handleOpenDialog(org)}
                        disabled={loading}
                      >
                        検証する
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          検証済み組織 ({organizations.length - pendingOrgs.length})
        </Typography>
        
        {organizations.length - pendingOrgs.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            検証済みの組織はありません。
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {organizations
              .filter(org => !needsVerification(org))
              .map((org) => (
                <Grid item xs={12} sm={6} md={4} key={org.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle1">{org.name}</Typography>
                        <Chip 
                          label={getStatusLabel(org.validation_status)} 
                          color={getStatusColor(org.validation_status) as any}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {getTypeLabel(org.organization_type)}
                      </Typography>
                      
                      <Typography variant="body2" noWrap>
                        <a href={org.url} target="_blank" rel="noopener noreferrer">{org.url}</a>
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
          </Grid>
        )}
      </Paper>
      
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          組織の検証: {selectedOrg?.name}
        </DialogTitle>
        
        <DialogContent>
          {selectedOrg && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body1" gutterBottom>
                <strong>URL:</strong> <a href={selectedOrg.url} target="_blank" rel="noopener noreferrer">{selectedOrg.url}</a>
              </Typography>
              
              <Typography variant="body1" gutterBottom>
                <strong>タイプ:</strong> {getTypeLabel(selectedOrg.organization_type)}
              </Typography>
              
              {selectedOrg.description && (
                <Typography variant="body1" gutterBottom>
                  <strong>説明:</strong> {selectedOrg.description}
                </Typography>
              )}
              
              {selectedOrg.validation_notes && (
                <Typography variant="body1" gutterBottom>
                  <strong>LLM検証メモ:</strong> {selectedOrg.validation_notes}
                </Typography>
              )}
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="検証メモ"
                value={verificationNotes}
                onChange={(e) => setVerificationNotes(e.target.value)}
                margin="normal"
              />
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog} color="default">
            キャンセル
          </Button>
          
          <Button 
            onClick={() => handleVerify(false)} 
            color="error"
            disabled={loading}
          >
            拒否
          </Button>
          
          <Button 
            onClick={() => handleVerify(true)} 
            color="primary"
            variant="contained"
            disabled={loading}
          >
            承認
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HumanVerificationPanel;
