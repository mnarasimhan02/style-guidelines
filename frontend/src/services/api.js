import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8001';

export const uploadFile = async (endpoint, file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_BASE_URL}${endpoint}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Upload error:', error);
    throw new Error(error.response?.data?.detail || error.message || 'Upload failed');
  }
};

export const uploadStyleGuide = async (file) => {
  return uploadFile('/upload/style-guide', file);
};

export const uploadCSR = async (file) => {
  return uploadFile('/upload/csr', file);
};
