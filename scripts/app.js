const { createApp } = Vue;

createApp({
    data() {
        return {
            title: "My flashcard app",
            username: '',
            password: '',
            token: localStorage.getItem('flashcards_token') || null,
            error: null,
            sections: [],

            showCreateSectionForm: false, // create section
            newSectionTitle: '',

            editingSectionId: null, // edit section
            editingSectionTitle: '',

            deletingSectionId: null, // delete section
            deleteReady: false,
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
                    localStorage.setItem('flashcards_token', this.token)
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
        },
        logout(){
            this.token = null;
            this.sections = [];
            this.error = null;
            localStorage.removeItem('flashcards_token');
        },
        //create_section
        async create_section(){
            const response = await fetch('http://localhost:8000/sections', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: this.newSectionTitle})
            });

            if(response.ok){
                const newSection = await response.json();
                this.sections.push(newSection);
                this.newSectionTitle = ''
            }
        },
        //Temp func for opening
        open_section(id) {
            pass;
        },
        // Edit section
        startEdit(section) {
            pass;
        },
        async delete_section(id){
            const response = await fetch (`http://localhost:8000/sections/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if(response.ok){
                this.sections = this.sections.filter(s => s.id !== id) //filtering deleted section
            }
        },
        request_delete(id){
            if(this.deletingSectionId !== id){
                this.deletingSectionId = id;
                this.deleteReady = false;

                setTimeout(() => {
                    if(this.deletingSectionId === id){
                        this.deleteReady = true;
                    }
                }, 500);

                setTimeout(() => {
                    if(this.deletingSectionId === id){
                        this.deletingSectionId = null;
                        this.deleteReady = false;
                    }
                }, 2000);
            } else if(this.deletingSectionId === id && this.deleteReady){
                this.delete_section(id);
                this.deletingSectionId = null;
                this.deleteReady = false;
            }
        }
    }
}).mount('#app');