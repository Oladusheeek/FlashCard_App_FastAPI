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
        start_edit_section(section){
            this.editingSectionId = section.id;
            this.editingSectionTitle = section.title
        },
        // Edit section
        async edit_section(section_id){
            try{
                const response = await fetch(`http://localhost:8000/sections/${section_id}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({title : this.editingSectionTitle})
                })

                if(response.ok){
                    const UpdatedSection = await response.json()
                    const SectionToUpdate = this.sections.find(s => s.id === section_id)
                    if (SectionToUpdate){
                        SectionToUpdate.title = UpdatedSection.title
                    }
                    this.error = null
                    this.editingSectionId = null
                    this.editingSectionTitle = ''
                } else {
                    this.error = 'Cannot edit sections data!'
                    if(response.status === 401){
                        this.token = null;
                    }
                }
            }
            catch (err){
                this.error = 'Cannot connect to the server. Ensure connectivity'
            }
        },
        async delete_section(section_id){
            const response = await fetch (`http://localhost:8000/sections/${section_id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if(response.ok){
                this.sections = this.sections.filter(s => s.id !== section_id) //filtering deleted section
            }
        },
        request_delete_section(section_id){
            if(this.deletingSectionId !== section_id){ //check if current 'id' equals saved 'delete id'
                this.deletingSectionId = section_id;
                this.deleteReady = false;

                setTimeout(() => { // pull off safety check after 0.5s
                    if(this.deletingSectionId === section_id){
                        this.deleteReady = true;
                    }
                }, 500);

                setTimeout(() => { // raise safety check after 3s
                    if(this.deletingSectionId === section_id){
                        this.deletingSectionId = null;
                        this.deleteReady = false;
                    }
                }, 3000);
            } else if(this.deletingSectionId === section_id && this.deleteReady){ // on second click on this exact button 
                this.delete_section(section_id);                                  // call delete func
                this.deletingSectionId = null;  //clear temp values
                this.deleteReady = false;       //
            }
        },
    }
}).mount('#app');