const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'src', 'components', 'Dashboard.js');

try {
  const content = fs.readFileSync(filePath, 'utf8');
  console.log(content.substring(0, 20000));
} catch (e) {
  console.error('Error:', e.message);
}
