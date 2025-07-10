import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

// Define types for our data structure
interface ProductVariant {
  serial: string;
  serial_alt: string;
  id: string;
  color: string;
  size: string;
  stock: number;
  price: number;
}

interface ProductInfo {
  serial_number: string;
  product_url: string;
  price_jp: number;
  jp_price_in_twd: number;
  product_list: ProductVariant[];
}

interface SearchHistoryItem {
  id: string;
  productId: string;
  alternativeProductId: string;
  productUrl: string;
  priceJPY: number;
  priceTWD: number;
  availableSizes: string;
  timestamp: Date;
}

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Load search history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('uniqlo-search-history');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save search history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('uniqlo-search-history', JSON.stringify(searchHistory));
  }, [searchHistory]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a product ID');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Make API call to Flask backend through nginx proxy
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const response = await axios.post(`${apiBaseUrl}api/search`, {
        product_id: searchQuery.trim()
      });

      const productData: ProductInfo | number = response.data;

      if (productData === -1 || typeof productData === 'number') {
        setError('Product not found');
        return;
      }

      // Group available sizes by color
      const availableStock = productData.product_list
        .filter(item => item.stock > 0)
        .reduce((acc, item) => {
          if (!acc[item.color]) {
            acc[item.color] = [];
          }
          acc[item.color].push(item.size);
          return acc;
        }, {} as Record<string, string[]>);

      const availableSizesString = Object.entries(availableStock)
        .map(([color, sizes]) => `${color}: ${sizes.join(', ')}`)
        .join(' | ');

      // Create new search history item
      const newHistoryItem: SearchHistoryItem = {
        id: Date.now().toString(),
        productId: productData.serial_number,
        alternativeProductId: productData.product_list[0]?.serial_alt || '',
        productUrl: productData.product_url,
        priceJPY: productData.price_jp,
        priceTWD: productData.jp_price_in_twd,
        availableSizes: availableSizesString,
        timestamp: new Date()
      };

      // Add to history (most recent first)
      setSearchHistory(prev => [newHistoryItem, ...prev.slice(0, 19)]); // Keep only last 20 searches
      setSearchQuery('');

    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search product. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat().format(price);
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleString();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 }, px: { xs: 1, sm: 2, md: 3 } }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: { xs: 3, md: 4 } }}>
          <Typography 
            variant="h3" 
            component="h1" 
            sx={{ 
              mb: 2, 
              fontWeight: 'bold',
              fontSize: { xs: '1.8rem', sm: '2.5rem', md: '3rem' }
            }}
          >
            UNIQLO 日本 🔴
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ fontSize: { xs: '1rem', md: '1.25rem' } }}>
            Search for product prices and stock availability
          </Typography>
        </Box>

        {/* Search Bar */}
        <Paper elevation={3} sx={{ p: { xs: 2, md: 3 }, mb: { xs: 3, md: 4 } }}>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              label="Product ID (6 digits)"
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., 474479"
              disabled={loading}
            />
            <Button
              variant="contained"
              size="large"
              onClick={handleSearch}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
              sx={{ minWidth: 120, width: { xs: '100%', sm: 'auto' } }}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Box>
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Paper>

        {/* Search History Table */}
        <Paper elevation={3}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h5" component="h2" sx={{ mb: 3, fontWeight: 'bold' }}>
              Search History
            </Typography>
            
            {searchHistory.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No search history yet. Try searching for a product!
                </Typography>
              </Box>
            ) : (
              <TableContainer sx={{ overflowX: 'auto' }}>
                <Table sx={{ minWidth: 650 }} size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ minWidth: 100 }}><strong>Product ID</strong></TableCell>
                      <TableCell sx={{ minWidth: 120 }}><strong>Alternative ID</strong></TableCell>
                      <TableCell sx={{ minWidth: 120 }}><strong>Product URL</strong></TableCell>
                      <TableCell align="right" sx={{ minWidth: 100 }}><strong>Price (JPY)</strong></TableCell>
                      <TableCell align="right" sx={{ minWidth: 100 }}><strong>Price (TWD)</strong></TableCell>
                      <TableCell sx={{ minWidth: 200 }}><strong>Available Sizes</strong></TableCell>
                      <TableCell sx={{ minWidth: 140, display: { xs: 'none', md: 'table-cell' } }}><strong>Search Time</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {searchHistory.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {item.productId}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {item.alternativeProductId}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="text"
                            size="small"
                            href={item.productUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{ fontSize: '0.75rem' }}
                          >
                            View
                          </Button>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold">
                            ¥{formatPrice(item.priceJPY)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold" color="primary">
                            NT${formatPrice(item.priceTWD)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {item.availableSizes ? (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {item.availableSizes.split(' | ').map((sizeInfo, index) => (
                                <Chip
                                  key={index}
                                  label={sizeInfo}
                                  size="small"
                                  variant="outlined"
                                  color="success"
                                  sx={{ fontSize: '0.7rem' }}
                                />
                              ))}
                            </Box>
                          ) : (
                            <Chip label="Out of Stock" size="small" color="error" />
                          )}
                        </TableCell>
                        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                          <Typography variant="body2" color="text.secondary">
                            {formatDate(item.timestamp)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;
