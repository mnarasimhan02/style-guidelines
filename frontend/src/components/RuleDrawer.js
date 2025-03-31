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
        key={rule.id || Math.random()} 
        sx={{ 
          p: 1, 
          my: 1, 
          borderRadius: 1,
          backgroundColor,
          border: '1px solid rgba(0, 0, 0, 0.12)'
        }}
      >
        <Typography variant="body2" gutterBottom>
          {rule.description}
        </Typography>
        {rule.examples && rule.examples.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" color="textSecondary">
              Examples:
            </Typography>
            {rule.examples.map((example, index) => (
              <Typography key={index} variant="caption" display="block" sx={{ ml: 1 }}>
                • {example}
              </Typography>
            ))}
          </Box>
        )}
        <Chip
          label={rule.type}
          size="small"
          sx={{
            mt: 1,
            backgroundColor: 'rgba(0, 0, 0, 0.08)',
            '& .MuiChip-label': {
              fontSize: '0.7rem',
            },
          }}
        />
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
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="subtitle1" component="span">
                  {category}
                </Typography>
                <Typography 
                  variant="caption" 
                  color="textSecondary" 
                  sx={{ ml: 1 }}
                >
                  ({rules.length} rules)
                </Typography>
              </Box>
            }
            secondary={
              <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                {tags.map((tag, index) => (
                  <Chip
                    key={index}
                    label={tag}
                    size="small"
                    variant="outlined"
                    sx={{
                      height: '20px',
                      '& .MuiChip-label': {
                        fontSize: '0.7rem',
                        px: 1,
                      },
                    }}
                  />
                ))}
              </Stack>
            }
          />
          {expandedCategories[category] ? <ExpandLess /> : <ExpandMore />}
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
      sx={{ width: 400 }}
      PaperProps={{ sx: { width: 400 } }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Style Guide Rules
        </Typography>
        <List>
          {Object.entries(rules).map(([category, categoryRules]) => (
            <React.Fragment key={category}>
              {renderCategoryHeader(category, categoryRules)}
              <Collapse in={expandedCategories[category]} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  <ListItem sx={{ flexDirection: 'column', alignItems: 'stretch', pl: 4 }}>
                    {categoryRules.map(rule => renderRule(rule))}
                  </ListItem>
                </List>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      </Box>
    </Drawer>
  );
};

export default RuleDrawer;
