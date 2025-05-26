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
