import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../constants/api';

function VerifyEmail() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('');
  const hasVerified = useRef(false);

  useEffect(() => {
    if (hasVerified.current) return;
    hasVerified.current = true;

    const verifyEmail = async () => {
      console.log('verifyEmail')
      try {
        const url = `${API_ENDPOINTS.MEMBER.VERIFY}/${token}`;
        console.log(url);
        const response = await fetch(url);
        const data = await response.json();
        
        if (response.ok) {
          setStatus('success');
          setMessage(data.message);
          setTimeout(() => navigate('/login'), 3000);
        } else {
          setStatus('error');
          setMessage(data.error);
        }
      } catch (error) {
        setStatus('error');
        setMessage('Failed to verify email');
      }
    };

    verifyEmail();
  }, [token, navigate]);

  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      {status === 'verifying' && <h2>Verifying your email...</h2>}
      {status === 'success' && (
        <>
          <h2>✅ Email Verified!</h2>
          <p>{message}</p>
          <p>Redirecting to login...</p>
        </>
      )}
      {status === 'error' && (
        <>
          <h2>❌ Verification Failed</h2>
          <p>{message}</p>
        </>
      )}
    </div>
  );
}

export default VerifyEmail;