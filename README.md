# Paper Crawler

### Usage

`usage: python main.py [--conference | -c CONFERENCE [CONFERENCE ...]] [--year | -y YEAR [YEAR ...]] [--keywords | -k KEYWORDS [KEYWORDS ...]]`

#### Special Arguments
- Mutiple conferences:  
    `-c CVPR NeurIPS ICLR`,  
    `-c CVPR,NeurIPS,ICLR`,  
    or `-c CVPR, NeurIPS, ICLR`
- All supported conferences (see conferences list below): `-c all`
- Multiple years:  
    `-y 2021 2022 2023`,  
    `-y 2021,2022,2023`,  
    `-y 2021, 2022, 2023`,  
    `-y 2021-2023`,  
    or `-y 2021~2023`

### Requirements

> bs4
>
> openpyxl
>
> tqdm
>
> requests

### Confereces
- Neural Information Processing Systems (NeurIPS ~2022)
- International Conference on Learning Representations (ICLR ~2023)
- European Conference on Computer Vision (ECCV 2018~2022)
- IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR ~2023)
- International Conference on Computer Vision (ICCV ~2021)
- International Conference on Machine Learning (ICML ~2023)
- Annual Meeting of the Assosication for Computational Linguistics (ACL 2018~2022)
- Conference on Empirical Methods in Natural Language Processing (EMNLP 2018~2022)
