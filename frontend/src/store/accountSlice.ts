import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

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

export const registerRecord = createAsyncThunk(
  'member/register',
  async (data: Omit<RegistrationRecord, 'id' | 'createdAt'>) => {
    const response = await fetch('http://localhost:5000/member', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error('Failed to create usage record')
    }

    return await response.json()
  }
)

export const loginRecord = createAsyncThunk(
  'member/login',
  async (data: Omit<RegistrationRecord, 'id' | 'createdAt' | 'firstName' | 'lastName'>) => {
    const response = await fetch('http://localhost:5000/member/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
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
        state.account = action.payload
      })
      .addCase(registerRecord.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to register account'
      })
      .addCase(loginRecord.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginRecord.fulfilled, (state, action) => {
        state.loading = false
        state.account = action.payload
      })
      .addCase(loginRecord.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to log in'
      })
  },
})

export const { clearError } = accountSlice.actions
export default accountSlice.reducer