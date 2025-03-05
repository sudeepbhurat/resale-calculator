import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Button,
  Box,
  Grid,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'https://resale-calculator.onrender.com/api';

function App() {
  const [formData, setFormData] = useState({
    original_price: '',
    age: '',
    category: '',
    condition: '',
  });
  const [categories, setCategories] = useState([]);
  const [conditions, setConditions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoadingData(true);
        const [categoriesRes, conditionsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/categories`),
          axios.get(`${API_BASE_URL}/conditions`),
        ]);
        console.log('Categories:', categoriesRes.data);
        console.log('Conditions:', conditionsRes.data);
        setCategories(categoriesRes.data);
        setConditions(conditionsRes.data);
        // Set initial values after data is loaded
        setFormData(prev => ({
          ...prev,
          category: categoriesRes.data[0] || '',
          condition: conditionsRes.data[0] || '',
        }));
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load categories and conditions. Please check if the backend server is running.');
      } finally {
        setIsLoadingData(false);
      }
    };
    fetchData();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/calculate`, {
        ...formData,
        original_price: parseFloat(formData.original_price),
        age: parseInt(formData.age),
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to calculate resale price');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Resale Price Calculator
        </Typography>

        {isLoadingData ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        ) : (
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Original Price"
                  name="original_price"
                  type="number"
                  value={formData.original_price}
                  onChange={handleChange}
                  required
                  InputProps={{
                    startAdornment: '₹',
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Age (years)"
                  name="age"
                  type="number"
                  value={formData.age}
                  onChange={handleChange}
                  required
                  inputProps={{ min: 0 }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                  disabled={isLoadingData || categories.length === 0}
                >
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Condition"
                  name="condition"
                  value={formData.condition}
                  onChange={handleChange}
                  required
                  disabled={isLoadingData || conditions.length === 0}
                >
                  {conditions.map((condition) => (
                    <MenuItem key={condition} value={condition}>
                      {condition.charAt(0).toUpperCase() + condition.slice(1)}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  type="submit"
                  disabled={loading || isLoadingData}
                  sx={{ py: 1.5 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Calculate Resale Price'}
                </Button>
              </Grid>
            </Grid>
          </form>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {result && (
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              Estimated Resale Price
            </Typography>
            <Typography variant="h3" color="primary">
              ₹{result.resale_price.toLocaleString()}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
              Based on {result.category} in {result.condition} condition after {result.age} years
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default App; 