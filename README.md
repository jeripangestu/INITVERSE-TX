
# InitVerse Mainnet Auto transactions Bot  

![Tampilan Bot](image.png)

## Getting Started  

### Prerequisites  

1. **Create an Account on InitVerse**  
   - Visit [InitVerse Candy]([https://candy.inichain.com/](https://candy.inichain.com/?invite=0x064Af2B49111642ED5AaC9B0Ea655f056AB03d7B) and connect your wallet.  
   - Link your social accounts and complete the "Start Here" task.  
   - Join the [miner pool](https://inichain.gitbook.io/initverseinichain/inichain/mining-mainnet) with the operating system of your choice (Windows/Linux).  
   - Acquire INI tokens by mining or receiving them from someone.  

### Setup  

Follow these steps to set up and run the bot.  

#### 1. Clone the Repository  
```bash
git clone https://github.com/jeripangestu/INITVERSE-TX.git
cd INITVERSE-TX
```

#### 2. Create and Activate a Virtual Environment  

**Windows:**  
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**  
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```

#### 4. Configure the Bot  
Create a `config.json` file in the project directory with the following structure:  
```json
{
  "private_keys": [
    "privatekey1",
    "privatekey2",
    "privatekey3"

  ],
  "timeout_after_trades": 1,
  "timeout_within_trades": 30,
  "send_amount": 0.000000015
}
```

#### 5. Run the Bot  
```bash
python main.py
```

## Features  

- Automated daily trading  


