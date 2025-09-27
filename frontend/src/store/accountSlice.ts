import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { API_ENDPOINTS } from '../constants/api';

export interface RegistrationRecord {
  id?: number
  email: string
  password: string
  firstName: string
  lastName: string
  createdAt?: string
}

interface RegistrationState {
  account: RegistrationRecord | null
  loading: boolean
  error: string | null
}

const initialState: RegistrationState = {
  account: null,
  loading: false,
  error: null,
}

export const accountRecord = createAsyncThunk(
  'member/account',
  async (data: Omit<RegistrationRecord, 'id' | 'createdAt'>) => {
    const response = await fetch(API_ENDPOINTS.MEMBER.ACCOUNT, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('Failed to get account data')
    }

    return await response.json()
  }
)

export const loginRecord = createAsyncThunk(
  'member/login',
  async (data: Omit<RegistrationRecord, 'id' | 'createdAt' | 'firstName' | 'lastName'>) => {
    const response = await fetch(API_ENDPOINTS.MEMBER.LOGIN, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    })

    if (!response.ok) {
      let errorMessage = 'Failed to log in'
      try {
        const errorData = await response.json()
        errorMessage = errorData.error || errorData.message || errorMessage
      } catch {
      }
      throw new Error(errorMessage)
    }

    return await response.json()
  }
)

export const logoutRecord = createAsyncThunk(
  'member/logout',
  async () => {
    const response = await fetch(API_ENDPOINTS.MEMBER.LOGOUT, {
      method: 'POST',
      credentials: 'include',
    })
    
    if (!response.ok) {
      throw new Error('Failed to logout')
    }
    
    return await response.json()
  }
)

export const registerRecord = createAsyncThunk(
  'member/register',
  async (data: Omit<RegistrationRecord, 'id' | 'createdAt'>) => {
    const response = await fetch(API_ENDPOINTS.MEMBER.REGISTER, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('Failed to register user')
    }

    return await response.json()
  }
)

const accountSlice = createSlice({
  name: 'account',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(registerRecord.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(registerRecord.fulfilled, (state, action) => {
        state.loading = false
        state.error = null
      })
      .addCase(registerRecord.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to register'
      })
      .addCase(loginRecord.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginRecord.fulfilled, (state, action) => {
        state.loading = false
        state.error = null
      })
      .addCase(loginRecord.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to log in'
      })
      .addCase(accountRecord.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(accountRecord.fulfilled, (state, action) => {
        state.loading = false
        state.account = action.payload
      })
      .addCase(accountRecord.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to get account'
      })
      .addCase(logoutRecord.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(logoutRecord.fulfilled, (state) => {
        state.loading = false
        state.account = null  // Clear account data
        state.error = null
      })
      .addCase(logoutRecord.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to log out'
      })
  },
})

export const { clearError } = accountSlice.actions
export default accountSlice.reducer