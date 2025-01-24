'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRouter } from 'next/navigation';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/auth/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            if (response.ok) {
                const data = await response.json();
                console.log(data);

                // Store email in localStorage
                localStorage.setItem('email', email);

                // Redirect to Verify page
                router.push('/verify');
            } else {
                const error = await response.json();
                console.error('Forgot password failed:', error);
                alert(error.detail || 'Forgot password failed.');
            }
        } catch (error) {
            console.error('Error during forgot password:', error);
            alert('Something went wrong. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-white/10 backdrop-blur-md rounded-lg p-8 shadow-lg"
        >
            <h2 className="text-2xl font-bold text-black mb-6 text-center">Forgot Password</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="email" className="text-black block mb-2">
                        Email
                    </label>
                    <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black focus:ring-black focus:ring-1 rounded-lg p-2 w-full"
                        required
                    />
                </div>

                <Button
                    type="submit"
                    className="w-full bg-black text-white rounded hover:bg-gray-900 transition-colors duration-300"
                    disabled={isLoading || !email}
                >
                    {isLoading ? 'Sending OTP...' : 'Send OTP'}
                </Button>
            </form>
        </motion.div>
    );
}
