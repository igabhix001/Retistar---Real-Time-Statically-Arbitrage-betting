'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export default function VerifyPage() {
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [isLoading, setIsLoading] = useState(false);
    const [isResending, setIsResending] = useState(false);
    const inputs = useRef<(HTMLInputElement | null)[]>([]);
    const router = useRouter();

    // Handle OTP input changes
    const handleChange = (element: HTMLInputElement, index: number) => {
        if (isNaN(Number(element.value))) return;

        setOtp([...otp.map((d, idx) => (idx === index ? element.value : d))]);

        // Move focus to the next field if the current field is filled
        if (element.value !== '') {
            if (index < 5) {
                inputs.current[index + 1]?.focus();
            }
        }
    };

    // Handle backspace key to move focus backwards
    const handleBackspace = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
        if (e.key === 'Backspace') {
            if (index > 0 && otp[index] === '') {
                inputs.current[index - 1]?.focus();
            }
        }
    };

    // Handle OTP form submission
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const email = localStorage.getItem('email');
            if (!email) {
                alert('Email not found. Please go back to Forgot Password.');
                return;
            }

            const response = await fetch('http://localhost:8000/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, otp: otp.join('') }),
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Verification successful:', data);
                router.push('/'); // Redirect to home after successful verification
            } else {
                const error = await response.json();
                console.error('Verification failed:', error);
                alert(error.detail || 'Verification failed.');
            }
        } catch (error) {
            console.error('Error during verification:', error);
            alert('Something went wrong. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // Handle OTP resend functionality
    const handleResendOTP = async (): Promise<void> => {
        setIsResending(true); // Show loading state for resend

        try {
            const email = localStorage.getItem('email');
            if (!email) {
                alert('Email not found. Please go back to Forgot Password.');
                return;
            }

            const response = await fetch('http://localhost:8000/auth/resend-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            if (response.ok) {
                const data = await response.json();
                console.log('OTP resent:', data);
                alert('A new OTP has been sent to your email.');
            } else {
                const error = await response.json();
                console.error('Resend OTP failed:', error);
                alert(error.detail || 'Failed to resend OTP.');
            }
        } catch (error) {
            console.error('Error during OTP resend:', error);
            alert('Something went wrong. Please try again.');
        } finally {
            setIsResending(false); // Reset loading state
        }
    };

    // Focus on the first OTP input when the page is loaded
    useEffect(() => {
        inputs.current[0]?.focus();
    }, []);

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-white/10 backdrop-blur-md rounded-lg p-8 shadow-lg"
        >
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Verify Your Account</h2>
            <p className="text-purple-200 text-center mb-6">
                We sent a verification code to your email. Please enter it below.
            </p>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex justify-center gap-2">
                    {otp.map((digit, index) => (
                        <input
                            key={index}
                            type="text"
                            ref={(el) => { inputs.current[index] = el; }}
                            value={digit}
                            onChange={(e) => handleChange(e.target, index)}
                            onKeyDown={(e) => handleBackspace(e, index)}
                            maxLength={1}
                            className="w-12 h-12 text-center text-2xl font-bold rounded-lg border border-purple-300/20 bg-white/5 text-white focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                        />
                    ))}
                </div>

                <Button
                    type="submit"
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white transition-colors duration-300"
                    disabled={isLoading || otp.includes('')}
                >
                    {isLoading ? 'Verifying...' : 'Verify Account'}
                </Button>
            </form>

            <div className="mt-6 text-center">
                <span className="text-purple-200">Didn't receive the code? </span>
                <button
                    className="text-purple-300 hover:text-white transition-colors duration-300 font-semibold"
                    onClick={handleResendOTP}
                    disabled={isResending}
                >
                    {isResending ? 'Resending...' : 'Resend'}
                </button>
            </div>
        </motion.div>
    );
}
