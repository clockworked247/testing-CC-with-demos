const User = require('../models/User');
const { generateToken, generateRefreshToken } = require('../middleware/auth');
const {
  validateUsername,
  validateEmail,
  validatePassword,
} = require('../utils/validation');
const { unauthorizedError, validationError } = require('../utils/errors');
const { asyncHandler } = require('../utils/errors');

/**
 * Register a new user
 * POST /api/auth/register
 */
exports.register = asyncHandler(async (req, res) => {
  const { username, email, password } = req.body;

  // Validate input
  const validatedUsername = validateUsername(username);
  const validatedEmail = validateEmail(email);
  const validatedPassword = validatePassword(password);

  // Create user
  const user = await User.create({
    username: validatedUsername,
    email: validatedEmail,
    password: validatedPassword,
  });

  // Generate tokens
  const token = generateToken(user);
  const refreshToken = generateRefreshToken(user);

  res.status(201).json({
    message: 'User registered successfully',
    token,
    refreshToken,
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      karma: user.karma,
      created_at: user.created_at,
    },
  });
});

/**
 * Login user
 * POST /api/auth/login
 */
exports.login = asyncHandler(async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    throw validationError('Username and password are required');
  }

  // Authenticate user
  const user = await User.authenticate(username, password);

  if (!user) {
    throw unauthorizedError('Invalid username or password');
  }

  // Check if email is verified (optional - can be enabled later)
  // if (!user.email_verified) {
  //   throw new APIError('Please verify your email before logging in', 403, ErrorCodes.EMAIL_NOT_VERIFIED);
  // }

  // Generate tokens
  const token = generateToken(user);
  const refreshToken = generateRefreshToken(user);

  res.json({
    message: 'Login successful',
    token,
    refreshToken,
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      karma: user.karma,
    },
  });
});

/**
 * Logout user
 * POST /api/auth/logout
 */
exports.logout = asyncHandler(async (req, res) => {
  // In a stateless JWT system, logout is handled client-side
  // For more security, you could maintain a token blacklist in Redis

  res.json({
    message: 'Logged out successfully',
  });
});

/**
 * Refresh token
 * POST /api/auth/refresh
 */
exports.refreshToken = asyncHandler(async (req, res) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    throw validationError('Refresh token is required');
  }

  // Verify refresh token
  const { verifyToken } = require('../middleware/auth');
  const decoded = verifyToken(refreshToken);

  if (decoded.type !== 'refresh') {
    throw unauthorizedError('Invalid refresh token');
  }

  // Get user
  const user = await User.findById(decoded.id);

  if (!user) {
    throw unauthorizedError('User not found');
  }

  // Generate new tokens
  const newToken = generateToken(user);
  const newRefreshToken = generateRefreshToken(user);

  res.json({
    token: newToken,
    refreshToken: newRefreshToken,
  });
});

/**
 * Verify email
 * POST /api/auth/verify-email
 */
exports.verifyEmail = asyncHandler(async (req, res) => {
  const { token } = req.body;

  if (!token) {
    throw validationError('Verification token is required');
  }

  // In a real implementation, you would:
  // 1. Decode the email verification token
  // 2. Verify it's valid and not expired
  // 3. Update the user's email_verified status

  // For this demo, we'll use a simple implementation
  const { verifyToken } = require('../middleware/auth');
  const decoded = verifyToken(token);

  await User.verifyEmail(decoded.id);

  res.json({
    message: 'Email verified successfully',
  });
});

/**
 * Get current user
 * GET /api/auth/me
 */
exports.getCurrentUser = asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id);

  if (!user) {
    throw unauthorizedError('User not found');
  }

  res.json({
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      karma: user.karma,
      about: user.about,
      created_at: user.created_at,
      email_verified: user.email_verified,
    },
  });
});
