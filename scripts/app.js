const { createApp } = Vue;

createApp({
    data() {
        return {
            title: "My flashcard app",
            username: '',
            password: '',
            token: null,
            error: null,
            sections: []
        }
    },
    mounted() {
        if(this.token){
            this.fetchSections();
        }
    },
    methods: {
        async login() {
            this.error = null;
            this.token = null;

            const formData = new URLSearchParams();
            formData.append('username', this.username);
            formData.append('password', this.password);

            try {
                const response = await fetch('http://localhost:8000/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: formData
                });
                const data = await response.json();
                this.password = '' //clearing password from cache

                if(!response.ok){
                    this.error = data.detail || 'Authorization error!'
                } else {
                    this.token = data.access_token;
                    this.fetchSections();
                }
            } 
            catch (err){
                this.error = 'Cannot connect to the server. Ensure connectivity'
            }
        },
        async fetchSections(){
            try {
                const response = await fetch('http://localhost:8000/sections', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if(response.ok){
                    this.sections = await response.json()
                    this.error = null
                } 
                else{
                    this.error = 'Cannot fetch sections data!'
                    if(response.status === 401){
                        this.token = null;
                    }
                }
                
            } 
            catch (err) {
                this.error = 'Cannot connect to the server. Ensure connectivity'
            }
        }
    }
}).mount('#app');