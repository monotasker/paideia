
import { doApiCall } from "../Services/utilityService";

const fetchTestimonials = async () => doApiCall({tag_list: [5]},
                                                "text_content",
                                                "JSON");
export {fetchTestimonials
}