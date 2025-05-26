import axios from 'axios';
import { Product, ProductFormData } from '../types/Product';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productService = {
  getAllProducts: async (): Promise<Product[]> => {
    const response = await api.get('/api/products');
    return response.data;
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get(`/api/products/${id}`);
    return response.data;
  },

  createProduct: async (product: ProductFormData): Promise<Product> => {
    const response = await api.post('/api/products', product);
    return response.data;
  },

  updateProduct: async (id: number, product: ProductFormData): Promise<Product> => {
    const response = await api.put(`/api/products/${id}`, product);
    return response.data;
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/api/products/${id}`);
  },
};
