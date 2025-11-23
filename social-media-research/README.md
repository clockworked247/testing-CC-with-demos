# Social Media Research Tool

Automated research tool for Instagram and TikTok that leverages the Apify API for data collection and OpenRouter API for AI-powered analysis. This tool can scrape videos, transcripts, and metadata from social media platforms and generate comprehensive research reports similar to Claude Code Deep Research.

## Features

- **Multi-Platform Support**: Scrape content from Instagram and TikTok
- **Flexible Scraping Modes**:
  - Account/Profile scraping: Analyze all content from a specific user
  - Search/Hashtag scraping: Find content based on keywords or hashtags
- **AI-Powered Analysis**: Uses OpenRouter API with Claude or other LLMs to analyze content
- **Comprehensive Reports**: Generates detailed research reports with:
  - Key themes and patterns
  - Engagement analysis
  - Trend identification
  - Actionable insights
- **Data Export**: Saves raw data, statistics, and formatted reports
- **Batch Processing**: Efficiently processes large quantities of content

## Prerequisites

- Python 3.8 or higher
- [Apify API key](https://console.apify.com/account/integrations)
- [OpenRouter API key](https://openrouter.ai/keys)

## Installation

1. Navigate to the project directory:
```bash
cd social-media-research
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
APIFY_API_KEY=your_apify_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Usage

### Basic Command Structure

```bash
python main.py --platform <platform> --mode <mode> --target <target> --research-question "<question>"
```

### Parameters

- `--platform`: Social media platform (`instagram` or `tiktok`)
- `--mode`: Scraping mode (`account` or `search`)
- `--target`: Username (for account mode) or search query/hashtag (for search mode)
- `--research-question`: Your research question (required for analysis)
- `--max-items`: Maximum number of items to scrape (default: 50)
- `--include-videos`: Include video file URLs in output
- `--no-analysis`: Skip LLM analysis and only save raw data
- `--output-dir`: Custom output directory (default: `output`)

### Examples

#### 1. Analyze Instagram Account

Research a specific Instagram user's content strategy:

```bash
python main.py \
  --platform instagram \
  --mode account \
  --target "natgeo" \
  --research-question "What content strategies does National Geographic use to drive engagement?" \
  --max-items 100
```

#### 2. Research Instagram Hashtag

Analyze content around a specific hashtag:

```bash
python main.py \
  --platform instagram \
  --mode search \
  --target "sustainability" \
  --research-question "What are the main themes in sustainability content on Instagram?" \
  --max-items 50
```

#### 3. Analyze TikTok Account

Research a TikTok creator's content:

```bash
python main.py \
  --platform tiktok \
  --mode account \
  --target "khaby.lame" \
  --research-question "What makes Khaby Lame's content so viral?" \
  --max-items 75
```

#### 4. TikTok Search/Trend Analysis

Research a trending topic:

```bash
python main.py \
  --platform tiktok \
  --mode search \
  --target "artificial intelligence" \
  --research-question "How is AI being discussed on TikTok?" \
  --max-items 100
```

#### 5. Data Collection Only

Scrape data without AI analysis (for later processing):

```bash
python main.py \
  --platform instagram \
  --mode account \
  --target "tesla" \
  --research-question "Tesla content analysis" \
  --no-analysis \
  --max-items 200
```

## Output

The tool generates three types of files in the output directory:

### 1. Raw Data (`raw_data_*.json`)
Complete JSON data of all scraped content including:
- Post/video metadata
- Captions/descriptions
- Engagement metrics (likes, comments, shares, views)
- URLs
- Timestamps

### 2. Statistics (`statistics_*.json`)
Summary statistics including:
- Total items scraped
- Platform breakdown
- Engagement totals and averages
- Date range of content

### 3. Research Report (`research_report_*.md`)
Comprehensive markdown report with:
- Executive summary
- Key findings and themes
- Engagement analysis
- Trends and patterns
- Recommendations
- Metadata about the research

## Configuration

### Environment Variables

You can customize behavior via environment variables in `.env`:

```bash
# Required
APIFY_API_KEY=your_key
OPENROUTER_API_KEY=your_key

# Optional
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
MAX_VIDEOS_PER_SEARCH=50
INCLUDE_VIDEO_FILES=false
OUTPUT_DIR=output
```

### Available LLM Models

The tool supports any model available on OpenRouter. Popular options:

- `anthropic/claude-3.5-sonnet` (default, recommended)
- `anthropic/claude-3-opus`
- `openai/gpt-4-turbo`
- `openai/gpt-4`
- `google/gemini-pro`

## Architecture

The tool is organized into modular components:

- `main.py`: CLI interface and workflow orchestration
- `config.py`: Configuration management
- `apify_scraper.py`: Apify API integration for Instagram and TikTok
- `llm_processor.py`: OpenRouter API integration and analysis
- `report_generator.py`: Report generation and data export

## Apify Actors Used

- **Instagram**: [apify/instagram-api-scraper](https://apify.com/apify/instagram-api-scraper)
- **TikTok**: [clockworks/tiktok-scraper](https://apify.com/clockworks/tiktok-scraper)

## Tips for Best Results

1. **Be Specific**: Craft clear, focused research questions
2. **Sample Size**: Use 50-100 items for quick insights, 200+ for comprehensive research
3. **Batch Processing**: The tool automatically batches large datasets for better LLM analysis
4. **Cost Management**: Start with smaller samples to test; LLM analysis costs scale with content
5. **Rate Limits**: Be mindful of Apify and OpenRouter rate limits for your account tier

## Troubleshooting

### "APIFY_API_KEY environment variable is required"
- Ensure `.env` file exists and contains your API key
- Check that you're running the command from the correct directory

### "Error calling OpenRouter API"
- Verify your OpenRouter API key is valid
- Check you have sufficient credits on your OpenRouter account
- Ensure the model name is correct

### No items found
- Verify the username or search query is correct
- Check that the account/content is public
- Try reducing `--max-items` if the scraper times out

## Cost Considerations

- **Apify**: Charges based on compute units; check [pricing](https://apify.com/pricing)
- **OpenRouter**: Charges per token; varies by model; check [pricing](https://openrouter.ai/docs#models)
- Typical research session (100 items): ~$0.50-$2.00 depending on configuration

## License

This tool is provided as-is for research and educational purposes. Ensure compliance with:
- Instagram and TikTok Terms of Service
- Apify Terms of Service
- OpenRouter Terms of Service
- Applicable data privacy regulations (GDPR, CCPA, etc.)

## Contributing

This is a standalone research tool. For modifications:
1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Support

For issues or questions:
- Check the Apify actor documentation
- Review OpenRouter API documentation
- Ensure all dependencies are correctly installed
- Verify API keys and permissions
