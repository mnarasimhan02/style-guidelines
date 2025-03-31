import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemText,
  Typography,
  Collapse,
  IconButton,
  Box,
  Chip,
} from '@mui/material';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';

const RuleDrawer = ({ open, onClose, rules }) => {
  const [expandedCategory, setExpandedCategory] = React.useState(null);

  const handleCategoryClick = (category) => {
    setExpandedCategory(expandedCategory === category ? null : category);
  };

  const getRuleTypeColor = (type) => {
    const colors = {
      DIRECT: 'primary',
      PATTERN: 'secondary',
      CONTEXT: 'warning',
      MULTI: 'info',
      CASE: 'success'
    };
    return colors[type] || 'default';
  };

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
          {Object.entries(rules || {}).map(([category, categoryRules]) => (
            <React.Fragment key={category}>
              <ListItem button onClick={() => handleCategoryClick(category)}>
                <ListItemText 
                  primary={category} 
                  secondary={`${categoryRules.length} rules`}
                />
                {expandedCategory === category ? <ExpandLess /> : <ExpandMore />}
              </ListItem>
              <Collapse in={expandedCategory === category} timeout="auto">
                <List component="div" disablePadding>
                  {categoryRules.map((rule) => (
                    <ListItem 
                      key={rule.id} 
                      sx={{ pl: 4 }}
                    >
                      <Box>
                        <Typography variant="body2" gutterBottom>
                          {rule.description}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Chip 
                            label={rule.type} 
                            size="small" 
                            color={getRuleTypeColor(rule.type)}
                            sx={{ mr: 1 }}
                          />
                          {rule.examples.length > 0 && (
                            <Chip 
                              label={`${rule.examples.length} examples`} 
                              size="small" 
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                    </ListItem>
                  ))}
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
