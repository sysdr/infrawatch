import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Container,
  Alert,
  CircularProgress,
  Box,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import ProductCard from './ProductCard';
import ProductForm from './ProductForm';
import { Product, ProductFormData } from '../../types/Product';
import { productService } from '../../services/api';

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productService.getAllProducts();
      setProducts(data);
      setError(null);
    } catch (err) {
      setError('Failed to load products. Make sure your backend is running.');
      // Mock data for development when backend is not available
      setProducts([
        {
          id: 1,
          name: 'Sample Product',
          price: 29.99,
          description: 'This is a sample product for development',
          category: 'Electronics',
          inStock: true,
          createdAt: new Date().toISOString(),
        },
        {
          id: 2,
          name: 'Demo Item',
          price: 49.99,
          description: 'Another demo product for testing the interface',
          category: 'Books',
          inStock: false,
          createdAt: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProduct = async (productData: ProductFormData) => {
    try {
      if (editingProduct) {
        await productService.updateProduct(editingProduct.id, productData);
      } else {
        await productService.createProduct(productData);
      }
      await loadProducts();
      setShowForm(false);
      setEditingProduct(null);
    } catch (err) {
      setError('Failed to save product');
    }
  };

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  const handleDeleteProduct = async (id: number) => {
    try {
      await productService.deleteProduct(id);
      await loadProducts();
    } catch (err) {
      setError('Failed to delete product');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" mt={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Product Management Dashboard
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowForm(true)}
          sx={{ mb: 3 }}
        >
          Add Product
        </Button>

        <Box sx={{ 
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)'
          },
          gap: 3,
          mt: 3
        }}>
          {products.map((product) => (
            <Box key={product.id}>
              <ProductCard
                product={product}
                onEdit={handleEditProduct}
                onDelete={handleDeleteProduct}
              />
            </Box>
          ))}
        </Box>

        <ProductForm
          open={showForm}
          product={editingProduct}
          onSave={handleSaveProduct}
          onClose={() => {
            setShowForm(false);
            setEditingProduct(null);
          }}
        />
      </Box>
    </Container>
  );
};

export default ProductList;
