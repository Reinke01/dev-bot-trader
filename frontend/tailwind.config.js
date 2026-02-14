/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: 'var(--color-bg)',
                card: 'var(--color-card)',
                primary: 'var(--color-primary)',
                secondary: 'var(--color-secondary)',
                danger: 'var(--color-danger)',
                success: 'var(--color-success)',
            },
        },
    },
    plugins: [],
}
