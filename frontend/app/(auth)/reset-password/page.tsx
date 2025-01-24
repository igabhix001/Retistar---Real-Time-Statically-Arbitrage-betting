'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRouter } from 'next/navigation';

export default function ResetPasswordPage() {
    const [email, setEmail] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, new_password: newPassword }),
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Password reset successful:', data);

                alert('Your password has been reset successfully. Please log in.');
                router.push('/login'); // Redirect to login page
            } else {
                const error = await response.json();
                console.error('Password reset failed:', error);
                alert(error.detail || 'Password reset failed.');
            }
        } catch (error) {
            console.error('Error during password reset:', error);
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
            <h2 className="text-2xl font-bold text-black mb-6 text-center">Reset Password</h2>
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
                        className="bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black w-full"
                        required
                    />
                </div>

                <div>
                    <label htmlFor="new-password" className="text-black block mb-2">
                        New Password
                    </label>
                    <Input
                        id="new-password"
                        type="password"
                        placeholder="Enter your new password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black w-full"
                        required
                    />
                </div>

                <Button
                    type="submit"
                    className="w-full bg-black text-white rounded hover:bg-gray-900 transition-colors duration-300"
                    disabled={isLoading || !email || !newPassword}
                >
                    {isLoading ? 'Resetting Password...' : 'Reset Password'}
                </Button>
            </form>
        </motion.div>
    );
}
