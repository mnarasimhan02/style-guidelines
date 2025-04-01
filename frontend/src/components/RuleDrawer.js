import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  Typography,
  Chip,
  Collapse,
  ListItemButton,
  Stack,
  Drawer,
} from '@mui/material';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';

const RuleTypeColors = {
  DIRECT: '#e3f2fd',  // Light Blue
  PATTERN: '#f3e5f5', // Light Purple
  CONTEXT: '#e8f5e9', // Light Green
  MULTI: '#fff3e0',   // Light Orange
  CASE: '#fce4ec',    // Light Pink
};

const CategoryTags = {
  STRUCTURE: ['sections', 'headings', 'tables'],
  NUMBERS: ['measurements', 'ranges', 'formatting'],
  DOMAIN: ['medical terms', 'company names'],
  FORMATTING: ['capitalization', 'spacing'],
  PUNCTUATION: ['commas', 'periods', 'colons'],
  GRAMMAR: ['sentence structure', 'tense'],
  ABBREVIATIONS: ['acronyms', 'short forms'],
  REFERENCES: ['citations', 'sources']
};

const RuleDrawer = ({ open = false, onClose = () => {}, rules = {} }) => {
  const [expandedCategories, setExpandedCategories] = useState({});

  const handleCategoryClick = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const renderRule = (rule) => {
    const backgroundColor = RuleTypeColors[rule.type] || '#f5f5f5';
    return (
      <Box 
        key={rule.id} 
        sx={{ 
          p: 2,
          mb: 1,
          borderRadius: 1,
          backgroundColor,
          '&:hover': {
            boxShadow: 1,
          }
        }}
      >
        <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
          Pattern: {rule.pattern}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Replacement: {rule.replacement}
        </Typography>
        {rule.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {rule.description}
          </Typography>
        )}
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Chip
            label={rule.type}
            size="small"
            sx={{ backgroundColor: RuleTypeColors[rule.type] }}
          />
          {rule.examples && rule.examples.length > 0 && (
            <Chip
              label={`${rule.examples.length} example${rule.examples.length > 1 ? 's' : ''}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Stack>
      </Box>
    );
  };

  const renderCategoryHeader = (category, rules) => {
    const tags = CategoryTags[category.toUpperCase()] || [];
    return (
      <Box>
        <ListItemButton onClick={() => handleCategoryClick(category)}>
          <ListItemText 
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="subtitle1">
                  {category} ({rules.length} rules)
                </Typography>
                {expandedCategories[category] ? <ExpandLess /> : <ExpandMore />}
              </Box>
            }
          />
        </ListItemButton>
      </Box>
    );
  };

  if (!rules || Object.keys(rules).length === 0) {
    return null;
  }

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: '400px',
          boxSizing: 'border-box',
          p: 2
        }
      }}
    >
      <Typography variant="h6" sx={{ mb: 2 }}>Style Guide Rules</Typography>
      <List>
        {Object.entries(rules).map(([category, categoryRules]) => (
          <React.Fragment key={category}>
            {renderCategoryHeader(category, categoryRules)}
            <Collapse in={expandedCategories[category]} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                <ListItem sx={{ display: 'flex', flexDirection: 'column', pl: 4 }}>
                  <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
                    {CategoryTags[category]?.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Stack>
                  {categoryRules.map(renderRule)}
                </ListItem>
              </List>
            </Collapse>
          </React.Fragment>
        ))}
      </List>
    </Drawer>
  );
};

export default RuleDrawer;
