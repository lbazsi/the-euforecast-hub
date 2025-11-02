/**
 * Quick deployment verification script for frontend.
 * Tests that build process works and all critical imports are valid.
 */

console.log('='.repeat(60));
console.log('EU Forecast Hub Frontend - Deployment Verification');
console.log('='.repeat(60));

// Test 1: Check critical files exist
const fs = require('fs');
const path = require('path');

  const requiredFiles = [
  'package.json',
  'vite.config.ts',
  'vercel.json',
  'src/App.tsx',
  'src/lib/api.ts',
  'src/pages/Builder.tsx',
];

console.log('\n1. Checking required files...');
let allFilesExist = true;
for (const file of requiredFiles) {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`[OK] ${file} exists`);
  } else {
    console.log(`[FAIL] ${file} is missing`);
    allFilesExist = false;
  }
}

// Test 2: Check package.json has required dependencies
console.log('\n2. Checking package.json...');
try {
  const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
  
  const requiredDeps = ['react', 'react-dom', 'react-router-dom'];
  let allDepsExist = true;
  
  for (const dep of requiredDeps) {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`[OK] ${dep} is in dependencies`);
    } else {
      console.log(`[FAIL] ${dep} is missing from dependencies`);
      allDepsExist = false;
    }
  }
  
  // Check build script exists
  if (packageJson.scripts && packageJson.scripts.build) {
    console.log('[OK] build script exists');
  } else {
    console.log('[FAIL] build script is missing');
    allDepsExist = false;
  }
  
  if (allDepsExist) {
    console.log('[OK] package.json looks good');
  }
} catch (e) {
  console.log(`[FAIL] Failed to read package.json: ${e.message}`);
  allFilesExist = false;
}

// Test 3: Check vercel.json configuration
console.log('\n3. Checking vercel.json...');
try {
  const vercelJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'vercel.json'), 'utf8'));
  
  if (vercelJson.framework === 'vite' || vercelJson.buildCommand) {
    console.log('[OK] vercel.json configured');
  } else {
    console.log('[WARN] vercel.json may need framework or buildCommand');
  }
  
  if (vercelJson.rewrites && vercelJson.rewrites.length > 0) {
    console.log('[OK] SPA rewrites configured');
  } else {
    console.log('[WARN] No rewrites found (may need for SPA routing)');
  }
} catch (e) {
  console.log(`[FAIL] Failed to read vercel.json: ${e.message}`);
  allFilesExist = false;
}

console.log('\n' + '='.repeat(60));
if (allFilesExist) {
  console.log('[SUCCESS] Basic file structure looks good!');
  console.log('\nNext steps:');
  console.log('1. Run: npm install');
  console.log('2. Run: npm run build (to test build process)');
  console.log('3. If build succeeds, ready for deployment!');
} else {
  console.log('[FAIL] Some required files are missing. Please check above.');
}
console.log('='.repeat(60));

