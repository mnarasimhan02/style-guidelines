import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Paper, Typography, Box, CircularProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { styled } from '@mui/material/styles';

const DropzoneContainer = styled(Paper)(({ theme, isdragactive, disabled }) => ({
  padding: theme.spacing(3),
  textAlign: 'center',
  cursor: disabled ? 'not-allowed' : 'pointer',
  border: `2px dashed ${disabled ? theme.palette.grey[300] : theme.palette.primary.main}`,
  backgroundColor: isdragactive === 'true' ? theme.palette.action.hover : theme.palette.background.default,
  opacity: disabled ? 0.6 : 1,
  '&:hover': {
    backgroundColor: disabled ? theme.palette.background.default : theme.palette.action.hover,
  },
}));

const FileUpload = ({ onUpload, accept, disabled = false, loading = false, success = false }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept === '.pdf' 
      ? { 'application/pdf': ['.pdf'] }
      : { 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    disabled: disabled || loading,
    multiple: false,
  });

  return (
    <DropzoneContainer
      {...getRootProps()}
      elevation={0}
      isdragactive={isDragActive.toString()}
      disabled={disabled || loading}
    >
      <input {...getInputProps()} />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {loading ? (
          <>
            <CircularProgress size={40} sx={{ mb: 2 }} />
            <Typography>Uploading...</Typography>
          </>
        ) : success ? (
          <>
            <CheckCircleIcon color="success" sx={{ fontSize: 40, mb: 2 }} />
            <Typography>File uploaded successfully!</Typography>
          </>
        ) : (
          <>
            <CloudUploadIcon sx={{ fontSize: 40, mb: 2, color: disabled ? 'text.disabled' : 'primary.main' }} />
            <Typography>
              {isDragActive
                ? 'Drop the file here'
                : 'Drag and drop a file here, or click to select'}
            </Typography>
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
              Accepted format: {accept === '.pdf' ? 'PDF' : 'DOCX'}
            </Typography>
          </>
        )}
      </Box>
    </DropzoneContainer>
  );
};

export default FileUpload;
