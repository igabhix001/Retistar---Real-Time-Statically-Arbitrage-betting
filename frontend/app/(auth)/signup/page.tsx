'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { Eye, EyeOff } from 'lucide-react';
import { motion } from 'framer-motion';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';

const formSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export default function SignUpPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
    },
  });

  interface FormValues {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
  }

  async function onSubmit(values: FormValues): Promise<void> {
    setIsLoading(true);
    try {
      console.log('Submitting values:', values); // Debug the payload
      const response = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const data: { detail?: string } = await response.json();
        console.log('Signup successful:', data);
        localStorage.setItem('email', values.email); // Store email for verification/resend
        window.location.href = '/verify';
      } else {
        const error: { detail?: string } = await response.json();
        console.error('Signup failed:', error);
        alert(error.detail || 'Signup failed');
      }
    } catch (error) {
      console.error('Error during signup:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-lg p-8 shadow-lg"
    >
      <h2 className="text-2xl font-bold text-black mb-6 text-center">Create Account</h2>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-black">First Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="John"
                      {...field}
                      className="bg-white/5 border-gray-300 text-black placeholder-gray-500 focus:border-black"
                    />
                  </FormControl>
                  <FormMessage className="text-red-300" />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-black">Last Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Doe"
                      {...field}
                      className="bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black"
                    />
                  </FormControl>
                  <FormMessage className="text-red-300" />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-black">Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="name@example.com"
                    {...field}
                    className="bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black"
                  />
                </FormControl>
                <FormMessage className="text-red-300" />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-black">Password</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      {...field}
                      className="bg-white border border-gray-300 text-black placeholder-gray-500 focus:border-black pr-10"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 text-gray-600 hover:text-black"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </FormControl>
                <FormMessage className="text-red-300" />
              </FormItem>
            )}
          />

          <Button
            type="submit"
            className="w-full bg-black text-white rounded hover:bg-gray-900 transition-colors duration-300"
            disabled={isLoading}
          >
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </Button>
        </form>
      </Form>

      <div className="mt-6 text-center text-sm">
        <span className="text-black">Already have an account? </span>
        <Link href="/login" className="text-black hover:text-gray-900 transition-colors duration-300">
          Log in
        </Link>
      </div>
    </motion.div>
  );
}
