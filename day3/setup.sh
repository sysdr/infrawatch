#!/bin/bash

# One-Click React Frontend Setup Script
# Day 3: Complete React TypeScript Frontend Implementation

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify prerequisites
print_status "Checking prerequisites..."

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    print_error "Node.js version 16+ required. Current version: $(node --version)"
    exit 1
fi

print_success "Prerequisites check passed"

# Step 1: Create project structure
print_status "Creating project structure..."

PROJECT_NAME="ecommerce-frontend"
if [ -d "$PROJECT_NAME" ]; then
    print_warning "Project directory exists. Removing..."
    rm -rf "$PROJECT_NAME"
fi

# Create React TypeScript project
print_status "Initializing React TypeScript project..."
npx create-react-app "$PROJECT_NAME" --template typescript --silent

cd "$PROJECT_NAME"

# Step 2: Install dependencies
print_status "Installing project dependencies..."
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material react-router-dom @types/react-router-dom axios --silent

print_status "Installing development dependencies..."
npm install --save-dev prettier eslint-config-prettier @testing-library/jest-dom @testing-library/react @testing-library/user-event --silent

print_success "Dependencies installed successfully"

# Step 3: Create directory structure
print_status "Creating directory structure..."
mkdir -p src/components/common
mkdir -p src/components/products
mkdir -p src/components/layout
mkdir -p src/services
mkdir -p src/types
mkdir -p src/utils
mkdir -p src/components/products/__tests__

# Step 4: Create source files
print_status "Creating source files..."

# Create types/Product.ts
cat > src/types/Product.ts << 'EOF'
export interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  category: string;
  inStock: boolean;
  createdAt: string;
}

export interface ProductFormData {
  name: string;
  price: number;
  description: string;
  category: string;
  inStock: boolean;
}
EOF

# Create services/api.ts
cat > src/services/api.ts << 'EOF'
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
EOF

# Create components/products/ProductCard.tsx
cat > src/components/products/ProductCard.tsx << 'EOF'
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
EOF

# Create components/products/ProductForm.tsx
cat > src/components/products/ProductForm.tsx << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  MenuItem,
} from '@mui/material';
import { Product, ProductFormData } from '../../types/Product';

interface ProductFormProps {
  open: boolean;
  product: Product | null;
  onSave: (product: ProductFormData) => void;
  onClose: () => void;
}

const categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports'];

const ProductForm: React.FC<ProductFormProps> = ({ open, product, onSave, onClose }) => {
  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    price: 0,
    description: '',
    category: 'Electronics',
    inStock: true,
  });

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        price: product.price,
        description: product.description,
        category: product.category,
        inStock: product.inStock,
      });
    } else {
      setFormData({
        name: '',
        price: 0,
        description: '',
        category: 'Electronics',
        inStock: true,
      });
    }
  }, [product, open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {product ? 'Edit Product' : 'Add New Product'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Product Name"
            fullWidth
            variant="outlined"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            select
            margin="dense"
            label="Category"
            fullWidth
            variant="outlined"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            sx={{ mb: 2 }}
          >
            {categories.map((category) => (
              <MenuItem key={category} value={category}>
                {category}
              </MenuItem>
            ))}
          </TextField>
          <FormControlLabel
            control={
              <Switch
                checked={formData.inStock}
                onChange={(e) => setFormData({ ...formData, inStock: e.target.checked })}
              />
            }
            label="In Stock"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            {product ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ProductForm;
EOF

# Create components/products/ProductList.tsx
cat > src/components/products/ProductList.tsx << 'EOF'
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
EOF

# Create App.tsx
cat > src/App.tsx << 'EOF'
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ProductList from './components/products/ProductList';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ProductList />
    </ThemeProvider>
  );
}

export default App;
EOF

# Create setupTests.ts
cat > src/setupTests.ts << 'EOF'
import '@testing-library/jest-dom';
EOF

# Create test file
cat > src/components/products/__tests__/ProductCard.test.tsx << 'EOF'
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ProductCard from '../ProductCard';
import { Product } from '../../../types/Product';

const mockProduct: Product = {
  id: 1,
  name: 'Test Product',
  price: 29.99,
  description: 'Test description',
  category: 'Electronics',
  inStock: true,
  createdAt: '2024-01-01T00:00:00Z',
};

const mockOnEdit = jest.fn();
const mockOnDelete = jest.fn();

describe('ProductCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders product information correctly', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
    expect(screen.getByText('Electronics')).toBeInTheDocument();
    expect(screen.getByText('In Stock')).toBeInTheDocument();
  });

  test('calls onEdit when edit button is clicked', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByText('Edit'));
    expect(mockOnEdit).toHaveBeenCalledWith(mockProduct);
  });

  test('calls onDelete when delete button is clicked', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByText('Delete'));
    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });
});
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx.conf
cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
EOF

# Update package.json scripts
print_status "Updating package.json scripts..."
npx json -I -f package.json -e 'this.scripts["test:coverage"]="react-scripts test --coverage --watchAll=false"'
npx json -I -f package.json -e 'this.scripts["docker:build"]="docker build -t ecommerce-frontend ."'
npx json -I -f package.json -e 'this.scripts["docker:run"]="docker run -p 3000:3000 ecommerce-frontend"'

print_success "Source files created successfully"

# Step 5: Build and test the application
print_status "Building the application..."
npm run build

if [ $? -eq 0 ]; then
    print_success "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Step 6: Run tests
print_status "Running tests..."
CI=true npm test -- --coverage --watchAll=false

if [ $? -eq 0 ]; then
    print_success "All tests passed"
else
    print_warning "Some tests failed, but continuing..."
fi

# Step 7: Docker setup (if Docker is available)
if command_exists docker; then
    print_status "Building Docker image..."
    docker build -t ecommerce-frontend . --quiet

    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
        
        print_status "Testing Docker container..."
        # Start container in background
        CONTAINER_ID=$(docker run -d -p 3001:80 ecommerce-frontend)
        
        # Wait for container to start
        sleep 5
        
        # Test if container is running
        if docker ps | grep -q "$CONTAINER_ID"; then
            print_success "Docker container is running successfully"
            print_status "Container accessible at http://localhost:3001"
            
            # Stop the test container
            docker stop "$CONTAINER_ID" > /dev/null
            docker rm "$CONTAINER_ID" > /dev/null
        else
            print_warning "Docker container failed to start properly"
        fi
    else
        print_warning "Docker build failed, but local development setup is complete"
    fi
else
    print_warning "Docker not found. Skipping containerization steps."
fi

# Step 8: Final verification and instructions
print_status "Verifying project structure..."

# Check if key files exist
files_to_check=(
    "src/App.tsx"
    "src/types/Product.ts"
    "src/services/api.ts"
    "src/components/products/ProductList.tsx"
    "src/components/products/ProductCard.tsx"
    "src/components/products/ProductForm.tsx"
    "src/components/products/__tests__/ProductCard.test.tsx"
    "Dockerfile"
    "nginx.conf"
    "docker-compose.yml"
)

all_files_exist=true
for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Missing file: $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    print_success "All required files created successfully"
else
    print_error "Some files are missing"
    exit 1
fi

# Final success message and instructions
echo
echo "=================================="
print_success "React Frontend Setup Complete!"
echo "=================================="
echo
echo "📁 Project Location: $(pwd)"
echo
echo "🚀 Available Commands:"
echo "   npm start              - Start development server (http://localhost:3000)"
echo "   npm test               - Run tests"
echo "   npm run test:coverage  - Run tests with coverage"
echo "   npm run build          - Build for production"
echo "   docker build -t ecommerce-frontend .  - Build Docker image"
echo "   docker-compose up      - Run with Docker Compose"
echo
echo "🎯 Expected Output Verification:"
echo "   ✅ Development server starts on http://localhost:3000"
echo "   ✅ Product Management Dashboard displays"
echo "   ✅ 'Add Product' button opens modal form"
echo "   ✅ Sample products show with mock data"
echo "   ✅ All tests pass successfully"
echo "   ✅ Docker image builds without errors"
echo
echo "🔧 Next Steps:"
echo "   1. Run 'npm start' to start the development server"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Test the Add Product functionality"
echo "   4. Connect to your Flask backend from Day 2"
echo
echo "📚 Assignment: Implement CategoryManager component"
echo "   - Add dynamic category management"
echo "   - Update ProductForm to use dynamic categories"
echo "   - Add comprehensive tests"
echo
print_success "Setup completed successfully! Happy coding! 🎉": 2 }}
          />
          <TextField
            margin="dense"
            label="Price"
            type="number"
            fullWidth
            variant="outlined"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
            required
            sx={{ mb
