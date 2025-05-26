import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
} from '@mui/material';
import { Product } from '../../types/Product';

interface ProductCardProps {
  product: Product;
  onEdit: (product: Product) => void;
  onDelete: (id: number) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onEdit, onDelete }) => {
  return (
    <Card sx={{ maxWidth: 345, margin: 1 }}>
      <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          {product.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {product.description}
        </Typography>
        <Box sx={{ mt: 2, mb: 1 }}>
          <Typography variant="h6" color="primary">
            ${product.price.toFixed(2)}
          </Typography>
          <Chip
            label={product.category}
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          />
          <Chip
            label={product.inStock ? 'In Stock' : 'Out of Stock'}
            color={product.inStock ? 'success' : 'error'}
            size="small"
          />
        </Box>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onEdit(product)}>
          Edit
        </Button>
        <Button size="small" color="error" onClick={() => onDelete(product.id)}>
          Delete
        </Button>
      </CardActions>
    </Card>
  );
};

export default ProductCard;
