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

// Configure axios to always send credentials
axios.defaults.withCredentials = true;

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
  product_id: string;
  product_name: string;
  price: string;
  colors: string[];
  sizes: string[];
  image_url: string;
  product_url: string;
  searched_at: string;
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

  // Load search history from backend on component mount
  useEffect(() => {
    loadSearchHistory();
  }, []);

  const loadSearchHistory = async () => {
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const response = await axios.get(`${apiBaseUrl}api/history`, {
        withCredentials: true // Important for session-based user identification
      });
      setSearchHistory(response.data.history || []);
    } catch (err) {
      console.error('Failed to load search history:', err);
    }
  };

  const clearSearchHistory = async () => {
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
      await axios.delete(`${apiBaseUrl}api/history`, {
        withCredentials: true
      });
      setSearchHistory([]);
    } catch (err) {
      console.error('Failed to clear search history:', err);
      setError('Failed to clear search history');
    }
  };

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
      }, {
        withCredentials: true // Important for session-based user identification
      });

      const productData: ProductInfo | number = response.data;

      if (productData === -1 || typeof productData === 'number') {
        setError('Product not found');
        return;
      }

      // Reload search history to include the new search
      await loadSearchHistory();
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
            <Box component="span" sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
              UNIQLO 日本
              <img 
                src="/frontend/uniqlo-jp-icon.png" 
                alt="UNIQLO JP" 
                style={{ width: '40px', height: '40px', objectFit: 'contain' }}
              />
            </Box>
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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
                Search History
              </Typography>
              {searchHistory.length > 0 && (
                <Button
                  variant="outlined"
                  size="small"
                  color="error"
                  onClick={clearSearchHistory}
                  sx={{ fontSize: '0.8rem' }}
                >
                  Clear History
                </Button>
              )}
            </Box>
            
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
                      <TableCell sx={{ minWidth: 200 }}><strong>Product Name</strong></TableCell>
                      <TableCell sx={{ minWidth: 120 }}><strong>Product URL</strong></TableCell>
                      <TableCell align="right" sx={{ minWidth: 100 }}><strong>Price</strong></TableCell>
                      <TableCell sx={{ minWidth: 150 }}><strong>Colors</strong></TableCell>
                      <TableCell sx={{ minWidth: 150 }}><strong>Sizes</strong></TableCell>
                      <TableCell sx={{ minWidth: 140, display: { xs: 'none', md: 'table-cell' } }}><strong>Search Time</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {searchHistory.map((item, index) => (
                      <TableRow key={`${item.product_id}-${index}`} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {item.product_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {item.product_name || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {item.product_url ? (
                            <Button
                              variant="text"
                              size="small"
                              href={item.product_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              sx={{ fontSize: '0.75rem' }}
                            >
                              View
                            </Button>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              N/A
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold" color="primary">
                            {item.price || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {item.colors && item.colors.length > 0 ? (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {item.colors.map((color, colorIndex) => (
                                <Chip
                                  key={colorIndex}
                                  label={color}
                                  size="small"
                                  variant="outlined"
                                  color="info"
                                  sx={{ fontSize: '0.7rem' }}
                                />
                              ))}
                            </Box>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              N/A
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {item.sizes && item.sizes.length > 0 ? (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {item.sizes.map((size, sizeIndex) => (
                                <Chip
                                  key={sizeIndex}
                                  label={size}
                                  size="small"
                                  variant="outlined"
                                  color="success"
                                  sx={{ fontSize: '0.7rem' }}
                                />
                              ))}
                            </Box>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              N/A
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(item.searched_at).toLocaleString()}
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
