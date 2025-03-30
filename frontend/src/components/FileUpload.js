import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Paper, Typography, Box } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { styled } from '@mui/material/styles';

const DropzoneContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  textAlign: 'center',
  cursor: 'pointer',
  border: `2px dashed ${theme.palette.primary.main}`,
  backgroundColor: theme.palette.background.default,
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const FileUpload = ({ onUpload, accept, disabled }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload]
  );

  // Convert file extensions to MIME types
  const acceptedTypes = {
    '.pdf': ['application/pdf'],
    '.docx': [
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword'
    ]
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    disabled,
    multiple: false,
  });

  const getAcceptedFileTypes = () => {
    return accept.split(',').map(ext => ext.trim()).join(', ');
  };

  return (
    <DropzoneContainer
      {...getRootProps()}
      elevation={0}
      sx={{ opacity: disabled ? 0.5 : 1 }}
    >
      <input {...getInputProps()} />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="body1" color="textSecondary">
          {isDragActive
            ? 'Drop the file here'
            : `Drag and drop a file here, or click to select`}
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          Accepted formats: {getAcceptedFileTypes()}
        </Typography>
      </Box>
    </DropzoneContainer>
  );
};

export default FileUpload;
