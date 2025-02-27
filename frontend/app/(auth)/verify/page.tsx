'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export default function VerifyPage() {
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [isLoading, setIsLoading] = useState(false);
    const [isResending, setIsResending] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const inputs = useRef<(HTMLInputElement | null)[]>([]);
    const router = useRouter();

    useEffect(() => {
        const email = localStorage.getItem('email');
        if (!email) {
            router.push('/login'); // Redirect if email is missing
        } else {
            inputs.current[0]?.focus(); // Focus on the first OTP input
        }
    }, [router]);

    const handleChange = (element: HTMLInputElement, index: number) => {
        const value = element.value.replace(/[^0-9]/g, ''); // Allow only numeric input
        if (value.length > 1) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        if (value && index < 5) {
            inputs.current[index + 1]?.focus(); // Move to the next input
        }
    };

    const handleBackspace = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
        if (e.key === 'Backspace' && index > 0 && otp[index] === '') {
            inputs.current[index - 1]?.focus(); // Move to the previous input
        }
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();
        

        if (otp.includes('')) {
            setErrorMessage('Please fill all OTP fields.');
            inputs.current[0]?.focus();
            return;
        }

        setIsLoading(true);
        setErrorMessage('');

        try {
            const email = localStorage.getItem('email');
            if (!email) {
                router.push('/login');
                return;
            }

            const response = await fetch('http://localhost:8000/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Ensure cookies are included
                body: JSON.stringify({ email, otp: otp.join('') }),
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Verification successful:', data);
                router.push('/dashboard'); // Redirect to the dashboard
            } else {
                const error = await response.json();
                console.error('Verification failed:', error);
                setOtp(['', '', '', '', '', '']); // Clear OTP fields
                setErrorMessage(error.detail || 'Invalid OTP. Please try again.');
            }
        } catch (error) {
            console.error('Unexpected error:', error);
            setErrorMessage('An unexpected error occurred. Please try again later.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleResendOTP = async () => {
        setIsResending(true);

        try {
            const email = localStorage.getItem('email');
            if (!email) {
                router.push('/login');
                return;
            }

            const response = await fetch('http://localhost:8000/auth/resend-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ email }),
            });

            if (response.ok) {
                alert('A new OTP has been sent to your email.');
            } else {
                const error = await response.json();
                console.error('Resend OTP failed:', error);
                alert(error.detail || 'Failed to resend OTP.');
            }
        } catch (error) {
            console.error('Unexpected error during OTP resend:', error);
            alert('Something went wrong. Please try again.');
        } finally {
            setIsResending(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-white/10 backdrop-blur-md rounded-lg p-8 shadow-lg"
        >
            <h2 className="text-2xl font-bold text-black mb-6 text-center">Verify Your Account</h2>
            <p className="text-black text-center mb-6">
                We sent a verification code to your email. Please enter it below.
            </p>

            {errorMessage && <p className="text-red-500 text-center mb-4">{errorMessage}</p>}

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex justify-center gap-2">
                    {otp.map((digit, index) => (
                        <input
                            key={index}
                            type="text"
                            aria-label={`OTP digit ${index + 1}`}
                            ref={(el) => {
                                inputs.current[index] = el;
                            }}
                            value={digit}
                            onChange={(e) => handleChange(e.target, index)}
                            onKeyDown={(e) => handleBackspace(e, index)}
                            maxLength={1}
                            className="w-12 h-12 text-center text-2xl font-bold rounded-lg bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black focus:ring-black"
                        />
                    ))}
                </div>

                <Button
                    type="submit"
                    className="w-full bg-black text-white rounded hover:bg-gray-900 transition-colors duration-300"
                    disabled={isLoading || otp.includes('')}
                >
                    {isLoading ? 'Verifying...' : 'Verify Account'}
                </Button>
            </form>

            <div className="mt-6 text-center">
                <span className="text-black">Didn't receive the code? </span>
                <button
                    className="text-black hover:text-gray-600 transition-colors duration-300 font-semibold"
                    onClick={handleResendOTP}
                    disabled={isResending}
                >
                    {isResending ? 'Resending...' : 'Resend'}
                </button>
            </div>
        </motion.div>
    );
}
