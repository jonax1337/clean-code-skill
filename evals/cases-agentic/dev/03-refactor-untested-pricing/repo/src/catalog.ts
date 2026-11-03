export type Category = "books" | "games" | "music";

export interface Product {
  sku: string;
  title: string;
  price: number;
  category: Category;
  stock: number;
}
