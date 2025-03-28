import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Paper, Grid, Alert, CircularProgress } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

interface UploadStatus {
  success: boolean;
  message: string;
}

interface AppliedRule {
  rule: string;
  type: string;
  section: string;
  examples: string[];
  confidence: number;
}

interface ResultItem {
  original_text: string;
  corrected_text: string | null;
  applied_rules: AppliedRule[];
}

interface DocumentStats {
  total_paragraphs: number;
  total_rules_applied: number;
}

interface Results {
  applied_rules: ResultItem[];
  document_stats: DocumentStats;
}

interface Progress {
  phase: string;
  current: number;
  total: number;
  message: string;
}

interface DocumentProgress {
  style_guide: Progress | null;
  csr: Progress | null;
}

// Helper function to parse and render text with change tags
const renderCorrectedText = (text: string | null) => {
  if (!text) return null;

  const parts = text.split(/(<change confidence=[\d.]+>|<\/change>)/);
  return parts.map((part, index) => {
    if (part.startsWith('<change confidence=')) {
      return null; // Skip the opening tag
    } else if (part === '</change>') {
      return null; // Skip the closing tag
    } else {
      const isChange = index > 0 && parts[index - 1]?.startsWith('<change confidence=');
      if (isChange) {
        const confidence = parseFloat(parts[index - 1].match(/confidence=([\d.]+)/)![1]);
        return (
          <Box key={index} sx={{ 
            display: 'inline',
            bgcolor: '#fff3cd',
            color: '#856404',
            px: 0.5,
            py: 0.25,
            borderRadius: 0.5,
            border: '1px dashed',
            borderColor: '#ffeeba',
            mx: 0.5
          }}>
            <Typography variant="body2" component="span" sx={{ 
              whiteSpace: 'pre-wrap',
              fontWeight: 500
            }}>
              {part}
            </Typography>
          </Box>
        );
      }
      return (
        <Typography variant="body2" component="span" sx={{ whiteSpace: 'pre-wrap' }}>
          {part}
        </Typography>
      );
    }
  });
};

function App() {
  const [styleGuideStatus, setStyleGuideStatus] = useState<UploadStatus | null>(null);
  const [csrStatus, setCsrStatus] = useState<UploadStatus | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [hasStyleGuide, setHasStyleGuide] = useState(false);
  const [progress, setProgress] = useState<DocumentProgress>({
    style_guide: null,
    csr: null
  });
  const [clientId] = useState(() => uuidv4());

  useEffect(() => {
    // Set up SSE connection for progress updates
    const eventSource = new EventSource(`/api/progress/${clientId}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(prev => ({
        ...prev,
        [data.document]: {
          phase: data.phase,
          current: data.current,
          total: data.total,
          message: data.message
        }
      }));
    };
    
    return () => {
      eventSource.close();
    };
  }, [clientId]);

  const onStyleGuideDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setProgress(prev => ({ ...prev, style_guide: null }));
    const formData = new FormData();
    formData.append('style_guide', file);

    try {
      const response = await axios.post('/api/upload-style-guide', formData, {
        headers: {
          'X-Client-Id': clientId
        }
      });
      if (response.data.success) {
        setStyleGuideStatus({
          success: true,
          message: `Successfully processed ${response.data.chunks} style guide chunks`
        });
        setHasStyleGuide(true);
      }
    } catch (error: any) {
      setStyleGuideStatus({
        success: false,
        message: error.response?.data?.error || 'Error uploading style guide'
      });
    } finally {
      setProgress(prev => ({ ...prev, style_guide: null }));
    }
  };

  const onCSRDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setProgress(prev => ({ ...prev, csr: null }));
    const formData = new FormData();
    formData.append('csr_doc', file);

    try {
      const response = await axios.post('/api/process-csr', formData, {
        headers: {
          'X-Client-Id': clientId
        }
      });
      if (response.data.success) {
        setCsrStatus({
          success: true,
          message: `Successfully processed CSR document (${response.data.results.document_stats.total_rules_applied} rules applied)`
        });
        setResults(response.data.results);
      }
    } catch (error: any) {
      setCsrStatus({
        success: false,
        message: error.response?.data?.error || 'Error uploading CSR document'
      });
    } finally {
      setProgress(prev => ({ ...prev, csr: null }));
    }
  };

  const styleGuideDropzone = useDropzone({
    accept: {
      'application/pdf': ['.pdf']
    },
    onDrop: onStyleGuideDrop,
    disabled: false
  });

  const csrDropzone = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    onDrop: onCSRDrop,
    disabled: !hasStyleGuide
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Text Comparison
      </Typography>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              1. Upload Style Guide
            </Typography>
            <Box
              {...styleGuideDropzone.getRootProps()}
              sx={{
                p: 3,
                border: '2px dashed',
                borderColor: styleGuideDropzone.isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 1,
                textAlign: 'center',
                cursor: 'pointer'
              }}
            >
              <input {...styleGuideDropzone.getInputProps()} />
              <Typography>
                Drag & drop your PDF style guide here, or click to select file
              </Typography>
            </Box>
            {progress.style_guide && (
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2" color="text.secondary">
                    {progress.style_guide.message}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" align="right">
                  {progress.style_guide.current} / {progress.style_guide.total}
                </Typography>
              </Box>
            )}
            {styleGuideStatus && (
              <Alert severity={styleGuideStatus.success ? 'success' : 'error'} sx={{ mt: 2 }}>
                {styleGuideStatus.message}
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, opacity: hasStyleGuide ? 1 : 0.5 }}>
            <Typography variant="h5" gutterBottom>
              2. Upload CSR Document
            </Typography>
            <Box
              {...csrDropzone.getRootProps()}
              sx={{
                p: 3,
                border: '2px dashed',
                borderColor: csrDropzone.isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 1,
                textAlign: 'center',
                cursor: hasStyleGuide ? 'pointer' : 'not-allowed'
              }}
            >
              <input {...csrDropzone.getInputProps()} />
              <Typography>
                Drag & drop your DOCX file here, or click to select file
              </Typography>
            </Box>
            {progress.csr && (
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2" color="text.secondary">
                    {progress.csr.message}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" align="right">
                  {progress.csr.current} / {progress.csr.total}
                </Typography>
              </Box>
            )}
            {csrStatus && (
              <Alert severity={csrStatus.success ? 'success' : 'error'} sx={{ mt: 2 }}>
                {csrStatus.message}
              </Alert>
            )}
          </Paper>
        </Grid>

        {results && (
          <>
            <Paper sx={{ p: 3, mt: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5">
                  Analysis Results
                </Typography>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Total Paragraphs: {results.document_stats.total_paragraphs}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Rules Applied: {results.document_stats.total_rules_applied}
                  </Typography>
                </Box>
              </Box>

              <Grid container spacing={3}>
                {/* Corrected Text Column */}
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="h6" gutterBottom>
                      Text Comparison
                    </Typography>
                    <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
                      <button
                        onClick={async () => {
                          try {
                            const response = await axios.post('/api/download-corrected', results, {
                              responseType: 'blob'
                            });
                            const url = window.URL.createObjectURL(new Blob([response.data]));
                            const link = document.createElement('a');
                            link.href = url;
                            link.setAttribute('download', 'corrected_document.docx');
                            document.body.appendChild(link);
                            link.click();
                            link.remove();
                            window.URL.revokeObjectURL(url);
                          } catch (error) {
                            console.error('Error downloading document:', error);
                          }
                        }}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: '#1976d2',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        Download Corrected Text (DOCX)
                      </button>
                      <button
                        onClick={async () => {
                          try {
                            const response = await axios.post('/api/download-analysis', results, {
                              responseType: 'blob'
                            });
                            const url = window.URL.createObjectURL(new Blob([response.data]));
                            const link = document.createElement('a');
                            link.href = url;
                            link.setAttribute('download', 'document_analysis.docx');
                            document.body.appendChild(link);
                            link.click();
                            link.remove();
                            window.URL.revokeObjectURL(url);
                          } catch (error) {
                            console.error('Error downloading document:', error);
                          }
                        }}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: '#2e7d32',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        Download Analysis (DOCX)
                      </button>
                    </Box>
                    {results.applied_rules
                      .filter(item => {
                        // Check if there are actual text changes by comparing original and corrected text
                        // after removing the XML-style change markers
                        if (!item.corrected_text) return false;
                        const cleanCorrectedText = item.corrected_text
                          .replace(/<change confidence=[\d.]+>/g, '')
                          .replace(/<\/change>/g, '');
                        return cleanCorrectedText.trim() !== item.original_text.trim();
                      })
                      .map((item, index) => (
                        <Paper key={index} sx={{ p: 2, mb: 2, bgcolor: 'white' }}>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" gutterBottom sx={{ 
                              color: 'primary.main',
                              display: 'flex',
                              alignItems: 'center',
                              gap: 1
                            }}>
                              <span style={{ 
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: '#1976d2',
                                color: 'white',
                                fontSize: '14px'
                              }}>
                                {index + 1}
                              </span>
                              Changed Section
                            </Typography>
                            <Box sx={{ 
                              p: 2, 
                              bgcolor: 'grey.50', 
                              borderRadius: 1,
                              border: '1px solid',
                              borderColor: 'grey.300',
                              mb: 2
                            }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Original Text:
                              </Typography>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {item.original_text}
                              </Typography>
                            </Box>
                            <Box sx={{ 
                              p: 2, 
                              bgcolor: '#f8f9fa', 
                              borderRadius: 1,
                              border: '1px solid',
                              borderColor: 'primary.light'
                            }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Corrected Text:
                              </Typography>
                              {item.corrected_text && renderCorrectedText(item.corrected_text)}
                            </Box>
                            <Box sx={{ mt: 2, p: 2, bgcolor: '#e8f5e9', borderRadius: 1, border: '1px solid #c8e6c9' }}>
                              <Typography variant="subtitle2" color="success.main" gutterBottom>
                                Changes Made:
                              </Typography>
                              <Typography variant="body2" component="div">
                                {item.applied_rules.map((rule, ruleIndex) => (
                                  <Box key={ruleIndex} sx={{ mb: 1 }}>
                                    • Changed "{rule.rule}" based on {rule.type} rule from "{rule.section}"
                                  </Box>
                                ))}
                              </Typography>
                            </Box>
                          </Box>
                        </Paper>
                      ))}
                    {/* Show message when no changes are needed */}
                    {results.applied_rules.length > 0 && 
                      results.applied_rules.every(item => {
                        if (!item.corrected_text) return true;
                        const cleanCorrectedText = item.corrected_text
                          .replace(/<change confidence=[\d.]+>/g, '')
                          .replace(/<\/change>/g, '');
                        return cleanCorrectedText.trim() === item.original_text.trim();
                      }) && (
                      <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Typography variant="body1" sx={{ color: 'success.main', fontStyle: 'italic' }}>
                          ✓ All sections follow the style guide - no changes needed
                        </Typography>
                      </Box>
                    )}
                  </Paper>
                </Grid>

                {/* Applied Rules Column */}
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="h6" gutterBottom>
                      Applied Rules
                    </Typography>
                    {results.applied_rules.map((item, index) => (
                      <Box key={index} sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" sx={{ mb: 1, color: 'text.secondary' }}>
                          Paragraph {index + 1}
                        </Typography>
                        <Box sx={{ pl: 2 }}>
                          {item.applied_rules.map((rule, ruleIndex) => (
                            <Paper 
                              key={ruleIndex} 
                              sx={{ 
                                p: 2, 
                                mb: 1, 
                                bgcolor: 'white',
                                borderLeft: 6,
                                borderColor: `rgba(255, 220, 100, ${0.3 + rule.confidence * 0.7})`
                              }}
                            >
                              <Grid container spacing={1}>
                                <Grid item xs={12}>
                                  <Typography variant="body2" color="primary">
                                    Rule Type: {rule.type}
                                  </Typography>
                                  <Typography variant="body2">
                                    Section: {rule.section}
                                  </Typography>
                                </Grid>
                                <Grid item xs={12}>
                                  <Typography variant="body2" sx={{ mt: 1 }}>
                                    <strong>Rule:</strong> {rule.rule}
                                  </Typography>
                                  {rule.examples.length > 0 && (
                                    <Box sx={{ mt: 1 }}>
                                      <Typography variant="body2">
                                        <strong>Examples:</strong>
                                      </Typography>
                                      <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                        {rule.examples.map((example, exIndex) => (
                                          <li key={exIndex}>
                                            <Typography variant="body2">
                                              {example}
                                            </Typography>
                                          </li>
                                        ))}
                                      </ul>
                                    </Box>
                                  )}
                                </Grid>
                              </Grid>
                            </Paper>
                          ))}
                        </Box>
                      </Box>
                    ))}
                  </Paper>
                </Grid>
              </Grid>
            </Paper>
          </>
        )}
      </Grid>
    </Container>
  );
}

export default App;
